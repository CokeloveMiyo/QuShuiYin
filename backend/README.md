# 清影 API

多平台媒体解析与下载代理服务。对外提供：

- `POST /api/parse` — 从分享文案中提取链接并解析
- `GET /api/stream` — 预览流代理
- `GET /api/download` — 下载代理

## 本地启动

```bash
pip install -r requirements.txt
python app.py
```

默认端口：`8051`

Docker：

```bash
docker compose up -d --build
```

## 配置

复制 `.env.example` 为 `.env`，按需填写 Cookie（多数公开分享链可不填）。

上游解析引擎致谢见仓库根目录 [NOTICE.md](../NOTICE.md)。
