# 部署说明（补充）

> 完整的首次部署步骤见根目录 `DEPLOYMENT_SUMMARY.md`，本文补充最新部署时的关键点。
> 新增的 `deploy/nginx.conf` 与 `deploy/supervisor.conf` 需要上传到服务器使用。

## 一、本次改动概要

本次「善后」主要完成了 **地图实时定位追踪**：

- 定位方式从浏览器原生 `navigator.geolocation` 改为**高德定位组件 `AMap.Geolocation`**（国内可用，支持 GPS / 基站 / Wi-Fi / IP 兜底定位），替换了原来在国内基本失效的定位逻辑。
- 新增「🛰️ 开启实时追踪」按钮，开启后：
  - 地图上出现蓝色定位圆点 + 精度圈，随移动实时刷新（`watchPosition` 持续追踪）；
  - 「🧭 跟随」开关打开时地图中心始终跟随当前位置；
  - 偏离已规划路线超过 40 米时**自动重新规划路线**，实现“走到哪路线追到哪”。
- 规划路线成功后自动开启实时追踪。
- 离开导航页时自动停止追踪，避免后台耗电。

## 二、HTTPS 是准确定位的前提（务必配置）

> 浏览器只在 HTTPS（或 localhost）下才允许网页调用高精度定位。
> **不配置 HTTPS 时**，定位仍可用，但只能退化为「IP 粗定位」（定位到城市/区级，无法“追着走”）。
> **配置 HTTPS 后**，手机打开网页即可获得与高德 App 一致的 GPS 级实时定位。

### 申请免费证书（Let's Encrypt）

```bash
sudo apt install -y certbot python3-certbot-nginx

# 先确保 nginx.conf 里的 server_name 已换成你的真实域名
sudo cp ~/sh-ai/deploy/nginx.conf /etc/nginx/sites-available/sh-ai
sudo ln -s /etc/nginx/sites-available/sh-ai /etc/nginx/sites-enabled/sh-ai
sudo nginx -t && sudo systemctl reload nginx

# 签发证书（会自动改写 nginx 配置）
sudo certbot --nginx -d yourdomain.com
```

签发完成后浏览器访问 `https://yourdomain.com` 即可获得准确定位。

## 三、上传部署时的注意事项

1. **前端 Key 白名单**：登录[高德开放平台](https://console.amap.com)，把 JS API 的 Key 域名白名单改为你的真实域名，同时确认安全密钥 `VITE_AMAP_SECURITY_CODE` 配置在 `frontend/.env.production` 中（当前已配置在 `frontend/.env`，构建时会读取）。
2. **重新构建前端**（改动生效）：
   ```bash
   cd frontend && npm install && npm run build
   ```
3. **后端 .env**：确认 `AMAP_API_KEY` 已配置为服务器端 Web 服务 Key。
4. **MySQL 域名/地址**：确认 `.env` 中 `DATABASE_URL` 指向服务器本机 MySQL。
5. **路径匹配**：`deploy/supervisor.conf` 中的 `/home/ubuntu/sh-ai` 和 `user=ubuntu` 需按服务器实际用户名/项目路径修改（例如阿里云 ecs-user 就改成 `/home/ecs-user/sh-ai`）。

## 四、部署文件清单

| 文件 | 作用 | 上传到服务器 |
|------|------|------|
| `deploy/nginx.conf` | Nginx 反代 + HTTPS 强制跳转 | `/etc/nginx/sites-available/sh-ai` |
| `deploy/supervisor.conf` | 后端进程守护 | `/etc/supervisor/conf.d/sh-ai.conf` |
| `frontend/dist/` | 前端构建产物 | `/var/www/sh-ai/frontend/dist/` |
| `app/ main.py requirements.txt` | 后端代码 | `~/sh-ai/` |
