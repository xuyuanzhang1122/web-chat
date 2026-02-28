# Fake-Ai 接入说明（webapp-conversation 底层）

本目录基于 `langgenius/webapp-conversation`，作为新的聊天前端底层框架。

## 本地启动

```bash
cd /Users/xumengyang/Downloads/web-chat/Fake-Ai/webchat-next
./start.sh
```

默认启动地址：`http://localhost:3000`

## 环境变量

首次启动会自动从 `.env.local.example` 复制 `.env.local`。
你可以手工编辑：

- `NEXT_PUBLIC_APP_ID`: 本地会话命名空间 ID
- `NEXT_PUBLIC_APP_KEY`: Dify App API Key
- `NEXT_PUBLIC_API_URL`: Dify API Base URL（例如 `http://115.29.149.96/v1`）

## URL 参数（已适配）

- `show_loading=0`: 关闭首屏 loading
- `theme=light|dark`: 强制主题（不传则跟随系统）

示例：

```text
http://localhost:3000/?show_loading=0&theme=light
```
