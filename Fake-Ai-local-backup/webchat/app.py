"""
Dify AI WebChat Backend
Flask application that proxies Dify API calls, manages conversation history via SQLite,
and streams AI responses to the frontend via SSE.
"""
from flask import Flask, request, Response, jsonify, render_template, stream_with_context
import requests
import sqlite3
import json
import uuid
import os
import threading
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")

# ─── Config ───────────────────────────────────────────────────────────────────
DIFY_API_KEY  = "app-w00kP2sCqXPHoE2x8W3uA5GU"
DIFY_BASE_URL = "http://115.29.149.96/v1"
DB_PATH       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webchat.db")

# Per-conversation stop events (keyed by local conversation id)
_stop_events: dict[str, threading.Event] = {}

# ─── Database ─────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with get_db() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id                   TEXT PRIMARY KEY,
                title                TEXT DEFAULT '新对话',
                dify_conversation_id TEXT,
                user_id              TEXT DEFAULT 'default_user',
                created_at           TEXT,
                updated_at           TEXT
            );
            CREATE TABLE IF NOT EXISTS messages (
                id               TEXT PRIMARY KEY,
                conversation_id  TEXT NOT NULL,
                role             TEXT NOT NULL,
                content          TEXT,
                files_json       TEXT,
                dify_message_id  TEXT,
                created_at       TEXT,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);
            CREATE INDEX IF NOT EXISTS idx_conv_updated  ON conversations(updated_at DESC);
        """)


# ─── Routes: static page ──────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ─── Routes: conversations ────────────────────────────────────────────────────

@app.route("/api/conversations", methods=["GET"])
def list_conversations():
    with get_db() as c:
        rows = c.execute(
            "SELECT * FROM conversations ORDER BY updated_at DESC LIMIT 200"
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/conversations", methods=["POST"])
def create_conversation():
    data = request.get_json(silent=True) or {}
    cid  = str(uuid.uuid4())
    now  = datetime.now().isoformat()
    title  = data.get("title", "新对话")[:80]
    user   = data.get("user", "default_user")
    with get_db() as c:
        c.execute(
            "INSERT INTO conversations (id, title, user_id, created_at, updated_at) VALUES (?,?,?,?,?)",
            (cid, title, user, now, now),
        )
    return jsonify({"id": cid, "title": title, "created_at": now, "updated_at": now})


@app.route("/api/conversations/<cid>", methods=["DELETE"])
def delete_conversation(cid):
    with get_db() as c:
        c.execute("DELETE FROM messages     WHERE conversation_id=?", (cid,))
        c.execute("DELETE FROM conversations WHERE id=?",             (cid,))
    return jsonify({"success": True})


@app.route("/api/conversations/<cid>/messages", methods=["GET"])
def get_messages(cid):
    with get_db() as c:
        rows = c.execute(
            "SELECT * FROM messages WHERE conversation_id=? ORDER BY created_at",
            (cid,),
        ).fetchall()
    out = []
    for r in rows:
        m = dict(r)
        try:
            m["files"] = json.loads(m["files_json"]) if m.get("files_json") else []
        except Exception:
            m["files"] = []
        out.append(m)
    return jsonify(out)


@app.route("/api/conversations/<cid>/title", methods=["PUT"])
def update_title(cid):
    data  = request.get_json(silent=True) or {}
    title = data.get("title", "新对话")[:80]
    now   = datetime.now().isoformat()
    with get_db() as c:
        c.execute(
            "UPDATE conversations SET title=?, updated_at=? WHERE id=?",
            (title, now, cid),
        )
    return jsonify({"success": True, "title": title})


# ─── Routes: chat ─────────────────────────────────────────────────────────────

@app.route("/api/chat/stop", methods=["POST"])
def stop_chat():
    data    = request.get_json(silent=True) or {}
    cid     = data.get("conversation_id")
    task_id = data.get("task_id")
    if cid and cid in _stop_events:
        _stop_events[cid].set()
    if task_id:
        try:
            requests.post(
                f"{DIFY_BASE_URL}/chat-messages/{task_id}/stop",
                headers={"Authorization": f"Bearer {DIFY_API_KEY}"},
                json={"user": data.get("user", "default_user")},
                timeout=5,
            )
        except Exception:
            pass
    return jsonify({"success": True})


@app.route("/api/chat", methods=["POST"])
def chat():
    data  = request.get_json(silent=True) or {}
    cid   = data.get("conversation_id")
    query = (data.get("query") or "").strip()
    files = data.get("files") or []
    user  = data.get("user") or "default_user"

    if not query:
        return jsonify({"error": "query is required"}), 400

    now = datetime.now().isoformat()

    # Create conversation if needed
    if not cid:
        cid   = str(uuid.uuid4())
        title = query[:60]
        with get_db() as c:
            c.execute(
                "INSERT INTO conversations (id, title, user_id, created_at, updated_at) VALUES (?,?,?,?,?)",
                (cid, title, user, now, now),
            )

    # Fetch dify conversation id
    with get_db() as c:
        row = c.execute(
            "SELECT dify_conversation_id FROM conversations WHERE id=?", (cid,)
        ).fetchone()
    dify_cid = (row["dify_conversation_id"] or "") if row else ""

    # Register stop event
    stop_evt = threading.Event()
    _stop_events[cid] = stop_evt

    # Save user message
    user_mid = str(uuid.uuid4())
    with get_db() as c:
        c.execute(
            "INSERT INTO messages (id, conversation_id, role, content, files_json, created_at)"
            " VALUES (?,?,?,?,?,?)",
            (user_mid, cid, "user", query, json.dumps(files) if files else None, now),
        )

    def generate():
        nonlocal dify_cid

        payload = {
            "inputs":            {},
            "query":             query,
            "response_mode":     "streaming",
            "conversation_id":   dify_cid,
            "user":              user,
        }
        if files:
            payload["files"] = files

        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type":  "application/json",
        }

        full_answer  = ""
        dify_task_id = None

        try:
            yield f"data: {json.dumps({'type':'start','conversation_id':cid})}\n\n"

            with requests.post(
                f"{DIFY_BASE_URL}/chat-messages",
                headers=headers,
                json=payload,
                stream=True,
                timeout=(10, 120),
            ) as resp:
                if resp.status_code != 200:
                    snippet = resp.text[:400]
                    yield f"data: {json.dumps({'type':'error','error':f'API错误({resp.status_code}): {snippet}'})}\n\n"
                    return

                for raw in resp.iter_lines():
                    if stop_evt.is_set():
                        yield f"data: {json.dumps({'type':'stopped'})}\n\n"
                        break
                    if not raw:
                        continue
                    line = raw.decode("utf-8", errors="ignore") if isinstance(raw, bytes) else raw
                    if not line.startswith("data: "):
                        continue
                    chunk_str = line[6:].strip()
                    if chunk_str in ("[DONE]", ""):
                        continue
                    try:
                        ev = json.loads(chunk_str)
                    except json.JSONDecodeError:
                        continue

                    etype = ev.get("event", "")

                    if etype in ("message", "agent_message"):
                        piece = ev.get("answer", "")
                        full_answer += piece
                        dify_cid     = ev.get("conversation_id") or dify_cid
                        dify_task_id = ev.get("task_id") or dify_task_id
                        if piece:
                            yield f"data: {json.dumps({'type':'chunk','content':piece,'task_id':dify_task_id})}\n\n"

                    elif etype in ("message_end", "agent_message_end"):
                        dify_cid   = ev.get("conversation_id") or dify_cid
                        dify_mid   = ev.get("id", "")
                        saved_at   = datetime.now().isoformat()
                        ai_mid     = str(uuid.uuid4())
                        with get_db() as c:
                            c.execute(
                                "INSERT INTO messages (id,conversation_id,role,content,dify_message_id,created_at)"
                                " VALUES (?,?,?,?,?,?)",
                                (ai_mid, cid, "assistant", full_answer, dify_mid, saved_at),
                            )
                            c.execute(
                                "UPDATE conversations SET dify_conversation_id=?, updated_at=? WHERE id=?",
                                (dify_cid, saved_at, cid),
                            )
                        with get_db() as c:
                            row2 = c.execute(
                                "SELECT title FROM conversations WHERE id=?", (cid,)
                            ).fetchone()
                        title = row2["title"] if row2 else "新对话"
                        yield f"data: {json.dumps({'type':'done','conversation_id':cid,'title':title})}\n\n"

                    elif etype == "error":
                        yield f"data: {json.dumps({'type':'error','error':ev.get('message','未知错误')})}\n\n"

                    elif etype == "ping":
                        pass  # keep-alive

        except requests.exceptions.ConnectionError:
            yield f"data: {json.dumps({'type':'error','error':'无法连接到AI服务，请检查网络连接'})}\n\n"
        except requests.exceptions.Timeout:
            yield f"data: {json.dumps({'type':'error','error':'请求超时，请稍后重试'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type':'error','error':f'系统错误: {str(e)[:200]}'})}\n\n"
        finally:
            _stop_events.pop(cid, None)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":    "no-cache",
            "X-Accel-Buffering":"no",
            "Connection":       "keep-alive",
        },
    )


# ─── Routes: file upload ──────────────────────────────────────────────────────

@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f    = request.files["file"]
    user = request.form.get("user", "default_user")
    try:
        resp = requests.post(
            f"{DIFY_BASE_URL}/files/upload",
            headers={"Authorization": f"Bearer {DIFY_API_KEY}"},
            files={"file": (f.filename, f.stream, f.content_type or "application/octet-stream")},
            data={"user": user},
            timeout=60,
        )
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.Timeout:
        return jsonify({"error": "上传超时，请重试"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Routes: audio-to-text ────────────────────────────────────────────────────

@app.route("/api/audio-to-text", methods=["POST"])
def audio_to_text():
    if "file" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    audio = request.files["file"]
    user  = request.form.get("user", "default_user")
    fname = audio.filename or "recording.webm"
    ctype = audio.content_type or "audio/webm"
    try:
        resp = requests.post(
            f"{DIFY_BASE_URL}/audio-to-text",
            headers={"Authorization": f"Bearer {DIFY_API_KEY}"},
            files={"file": (fname, audio.stream, ctype)},
            data={"user": user},
            timeout=30,
        )
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.Timeout:
        return jsonify({"error": "语音识别超时，请重试"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
