# 清影 · 免费部署指南

推荐拆成两半：**后端 API** + **前端静态站**。全部可走免费额度。

```text
用户浏览器
   │
   ▼
前端（Cloudflare Pages / Vercel）  ← 静态页面
   │  请求 /api/...
   ▼
后端（Render）                    ← Python 解析 + 下载代理
```

---

## 0. 先把代码推到 GitHub

1. 注册 [GitHub](https://github.com)，新建仓库（例如 `qingying`）
2. 在项目根目录执行：

```bash
git add .
git commit -m "feat: 清影无水印解析站点"
git branch -M main
git remote add origin https://github.com/你的用户名/qingying.git
git push -u origin main
```

---

## 1. 部署后端（Render · 免费）

1. 打开 [https://render.com](https://render.com) ，用 GitHub 登录  
2. **New → Web Service**，选中你的 `qingying` 仓库  
3. 填写：

| 项 | 值 |
| --- | --- |
| Root Directory | `backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn --workers 2 --bind 0.0.0.0:$PORT --timeout 120 app:app` |
| Plan | **Free** |

4. Environment（可选）：

```text
SECRET_KEY=随便一串随机字符
XIAOHONGSHU_COOKIE=   # 小红书需要时再填
```

5. 点 **Create Web Service**，等部署完成  
6. 记下地址，例如：`https://qingying-api.onrender.com`  
7. 浏览器打开该地址，应看到「清影 API」页面

> Free 实例约 **15 分钟无访问会休眠**，下次打开可能要等 30～60 秒冷启动，属正常现象。

也可用仓库根目录的 `render.yaml`：**New → Blueprint**，选仓库一键创建。

---

## 2. 部署前端（Cloudflare Pages · 免费，推荐）

1. 打开 [https://dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages** → **Create** → **Pages** → 连接 GitHub  
2. 选中同一仓库，配置：

| 项 | 值 |
| --- | --- |
| Framework preset | Vite |
| Root directory | `frontend` |
| Build command | `npm run build` |
| Build output directory | `dist` |

3. **Environment variables**（生产）增加：

| Name | Value |
| --- | --- |
| `VITE_API_BASE` | `https://qingying-api.onrender.com`（换成你的后端地址，**不要**末尾斜杠） |

4. 保存并部署。完成后会得到类似：  
   `https://qingying.pages.dev`

### 备选：Vercel

- Import 仓库 → Root Directory 选 `frontend`  
- Build：`npm run build`，Output：`dist`  
- Env：`VITE_API_BASE` = 你的 Render 后端地址  

### 备选：GitHub Pages

适合纯静态，但要自己配 Actions；且 Pages **不能**跑 Python。前端仍须把 `VITE_API_BASE` 指到 Render。

---

## 3. 验证

1. 打开前端网址  
2. 粘贴一条抖音 / B 站分享链接 → 解析  
3. 能预览并下载即成功  

若解析失败：

- 打开浏览器 F12 → Network，看 `/api/parse` 是否打到了 Render 域名  
- 确认 `VITE_API_BASE` 写对且已重新 **Build**（改环境变量后必须重新部署前端）  
- Render 若刚醒，等冷启动完成再试  

---

## 4. 费用与限制（心里有数）

| 平台 | 免费点 | 注意 |
| --- | --- | --- |
| Render Free | Web Service 可跑 | 休眠、带宽有限、超时约 100s |
| Cloudflare Pages | 静态站几乎无限 | 只适合前端 |
| Vercel Hobby | 静态/前端够用 | 同样只适合前端 |

本项目的「解析 + 代理下载」**必须**有后端，不能只丢到 GitHub Pages。

---

## 5. 本地对照

| 环境 | 前端 API |
| --- | --- |
| 本地 `npm run dev` | 不设 `VITE_API_BASE`，走 Vite 代理到 `127.0.0.1:8051` |
| 线上 | 必须设 `VITE_API_BASE=https://你的后端` |

---

## 6. 可选：一键脚本备忘

后端启动命令（Render）：

```bash
gunicorn --workers 2 --bind 0.0.0.0:$PORT --timeout 120 app:app
```

前端构建：

```bash
cd frontend
npm install
VITE_API_BASE=https://你的后端.onrender.com npm run build
```
