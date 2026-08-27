# QuShuiYin · 清影

> 一键解析抖音、快手、B 站、YouTube、小红书等平台的无水印视频与图集

粘贴分享口令即可自动提取链接、在线预览、保存到本地。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📸 界面预览

![清影 QuShuiYin 界面预览](./docs/preview.png)

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

### 环境变量（`backend/.env`）

复制 `backend/.env.example` 为 `backend/.env`：

```env
SECRET_KEY=随机字符串
XIAOHONGSHU_COOKIE=a1=xxx; webId=xxx; web_session=xxx
DOUBAO_COOKIE=
```

> **小红书 Cookie 格式**：选 **Header String**（请求头字符串），不是 JSON、不是 Netscape。  
> 从浏览器 F12 → 网络 → 请求头里复制 `Cookie:` 后面的整段，原样粘贴，一行即可。

## ☁️ 免费部署（网站上线）

架构：**Render 跑后端 + Cloudflare Pages 跑前端**

```text
用户 → Cloudflare Pages（网页）→ Render（API）→ 各视频平台
```

### ① 部署后端 — [Render](https://render.com)

| 配置项 | 值 |
|--------|-----|
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn --workers 2 --bind 0.0.0.0:$PORT --timeout 120 app:app` |
| Plan | Free |

环境变量（可选）：

```text
SECRET_KEY=随机字符串
XIAOHONGSHU_COOKIE=Header String 格式的 Cookie
```

部署完成后记下地址，例如：`https://qushuiyin-api.onrender.com`

### ② 部署前端 — [Cloudflare Pages](https://dash.cloudflare.com)

| 配置项 | 值 |
|--------|-----|
| 框架预设 | **无 / None**（不要选 VitePress） |
| 根目录 | `frontend` |
| 构建命令 | `npm install && npm run build` |
| 输出目录 | `dist` |

环境变量（**必填**）：

| 变量名 | 值 |
|--------|-----|
| `VITE_API_BASE` | `https://你的render地址.onrender.com`（末尾不要 `/`） |

部署完成后访问 `https://xxx.pages.dev` 即可。

> 更详细的图文步骤见 **[DEPLOY.md](./DEPLOY.md)**

### 备选前端平台

[Vercel](https://vercel.com)：Root Directory 填 `frontend`，同样设置 `VITE_API_BASE`。

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

## ❓ 常见问题

| 问题 | 解决办法 |
|------|----------|
| 网页能开，解析失败 | 检查 `VITE_API_BASE` 是否指向 Render 后端，改后需重新部署前端 |
| Render 第一次很慢 | 免费实例会休眠，等 30～60 秒冷启动 |
| 小红书解析失败 | 使用带 `xsec_token` 的完整分享链接，或配置 `XIAOHONGSHU_COOKIE` |
| B 站无法下载 | 确保后端已更新到最新版（CDN 直链 + 代理下载） |
| Cloudflare 没有 Vite 预设 | 选「无」，手动填构建命令和 `dist` |

## ⚠️ 免责声明

- 本项目**仅供学习交流与技术研究**
- 请遵守各平台服务条款与当地法律法规
- 请勿用于侵权、商用或任何违法用途
- 后端解析引擎衍生自开源项目，详见 [NOTICE.md](./NOTICE.md)

## 📄 License

[MIT](LICENSE)
