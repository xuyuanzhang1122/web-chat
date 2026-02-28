# web-chat

一个基于 Dify API 的 AI 聊天应用集合，包含 Python 后端、Next.js 前端及桌面客户端。

## 项目结构

```
web-chat/
├── Fake-Ai/                  # 主项目：AI 聊天代理应用
│   ├── webchat/              # Flask 后端（代理 Dify API，SSE 流式输出）
│   ├── webchat-next/         # Next.js 前端（基于 webapp-conversation）
│   ├── DeepSeek/             # DeepSeek 相关模块
│   ├── fake_openwebui.py     # 桌面 GUI 主程序
│   ├── fake_openwebui_cli.py # 命令行版本
│   └── fake_openwebui_gui.py # GUI 版本
├── Fake-Ai-local-backup/     # Fake-Ai 本地备份
├── open-webui-main/          # Open WebUI（第三方开源组件）
└── webapp-conversation/      # Next.js 聊天前端（基于 langgenius/webapp-conversation）
```

## 快速开始

### Flask 后端（webchat）

```bash
cd Fake-Ai/webchat
pip install -r requirements.txt
python app.py
# 访问 http://localhost:5000
```

### Next.js 前端（webchat-next）

```bash
cd Fake-Ai/webchat-next
cp .env.local.example .env.local
# 编辑 .env.local，填入你的 Dify 配置
./start.sh
# 访问 http://localhost:3000
```

### webapp-conversation 前端

```bash
cd webapp-conversation
cp .env.example .env
# 编辑 .env，填入你的 Dify 配置
pnpm install
pnpm dev
```

## 环境变量配置

在 `webchat-next/.env.local` 或 `webapp-conversation/.env` 中配置：

| 变量 | 说明 |
|------|------|
| `NEXT_PUBLIC_APP_ID` | 应用 ID（本地命名空间） |
| `NEXT_PUBLIC_APP_KEY` | Dify App API Key |
| `NEXT_PUBLIC_API_URL` | Dify API 地址，例如 `http://your-server/v1` |

## 技术栈

- **后端**：Python / Flask / SQLite
- **前端**：Next.js / Tailwind CSS
- **AI 服务**：Dify API（支持流式 SSE 输出）
- **桌面端**：PyQt（GUI）

## 版本

- v1.0 — 初始版本

## 开发者

- 开发者 QQ：1571032052
