# QuShuiYin · 清影

> 一键解析抖音、快手、B 站、YouTube、小红书等平台的无水印视频与图集

粘贴分享口令即可自动提取链接、在线预览、保存到本地。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ 功能特性

- **智能抽链** — 分享文案里夹杂文字也能自动识别 URL
- **多平台支持** — 抖音 / 快手 / B 站 / YouTube / 小红书 / TikTok / 微博等
- **在线预览** — 视频、图集、实况、音频均可预览
- **代理下载** — 服务端代理，缓解防盗链与跨域问题
- **简洁界面** — 现代交互设计，支持粘贴、清空、一键解析

## 🖼️ 使用流程

1. 复制平台分享链接或口令
2. 粘贴到输入框，点击「开始解析」
3. 预览内容后点击「保存」下载到本地

## 🛠️ 技术栈

| 模块 | 技术 |
|------|------|
| 前端 | Vite · React · TypeScript · Framer Motion |
| 后端 | Flask · Gunicorn · 多平台 Parser 工厂 |

## 🚀 本地运行

### 环境要求

- Python 3.8+
- Node.js 18+

### 1. 启动后端（端口 8051）

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 2. 启动前端（端口 5173）

```bash
cd frontend
npm install
npm run dev
```

浏览器访问：**http://localhost:5173**

Windows 用户也可双击根目录 `start.bat` 一键启动。

### 可选配置

复制 `backend/.env.example` 为 `backend/.env`，按需填写：

```env
SECRET_KEY=随机字符串
XIAOHONGSHU_COOKIE=   # 部分小红书链接需要
DOUBAO_COOKIE=
```

## ☁️ 免费部署

本项目需**前后端分离部署**（GitHub Pages 只能托管静态页，无法跑解析后端）。

| 组件 | 推荐平台 | 说明 |
|------|----------|------|
| 后端 API | [Render](https://render.com) Free | 跑 Flask 解析服务 |
| 前端站点 | [Cloudflare Pages](https://pages.cloudflare.com) / Vercel | 静态页面 |

前端生产环境需设置环境变量：

```text
VITE_API_BASE=https://你的后端地址.onrender.com
```

完整部署教程见 **[DEPLOY.md](./DEPLOY.md)**。

## 📁 项目结构

```text
QuShuiYin/
├── frontend/          # React 前端
├── backend/           # Flask 解析 API
│   ├── src/parsers/   # 各平台解析器
│   └── src/api/       # parse / stream / download 接口
├── DEPLOY.md          # 部署指南
├── NOTICE.md          # 第三方开源致谢
└── render.yaml        # Render 一键部署配置
```

## 🔌 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/parse` | 解析分享链接 |
| GET | `/api/stream` | 媒体预览代理 |
| GET | `/api/download` | 媒体下载代理 |

## ⚠️ 免责声明

- 本项目**仅供学习交流与技术研究**
- 请遵守各平台服务条款与当地法律法规
- 请勿用于侵权、商用或任何违法用途
- 后端解析引擎衍生自开源项目，详见 [NOTICE.md](./NOTICE.md)

## 📄 License

[MIT](LICENSE)
