## 功能简介
- 模拟AI对话，无需连接任何API。
- 超过三次提问后会弹出一个窗口，并连接到本地部署的deepseek-r1:1.5b模型，仅供娱乐。

## 系统要求
- 目前仅支持Windows系统。

## 开发者信息
- 该程序由开发者和AI共同开发，如有问题请联系QQ：1571032052。

## 使用教程
- 点击打开后内置几个固定问答，例如“你好，你是谁”等。其他回答会提示“服务器繁忙”，超过三次问答会弹窗。

## 模型说明
- 使用deepseek-r1:1.5b模型，仅供娱乐，不适用于生产力AI。电脑休眠会断开端口转发服务，所以在线AI是随机的。

## 技术栈
- 本项目使用Python编写。

## Web 前端（新底层框架）
- 已接入 `langgenius/webapp-conversation` 到目录 `webchat-next`。
- 启动方式：
  - `cd webchat-next`
  - `./start.sh`
- 详细说明见 `webchat-next/README_FAKE_AI.md`。
