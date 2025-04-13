# brush-captcha - 自建打码平台

本项目基于 Camoufox 指纹伪装方案，包含前端页面、后端 API 服务和分布式打码客户端，支持多实例并发运行。目前仅支持了Turnstile，后续根据实际项目需要将继续集成其他类型打码。

---
### ✅ 验支持一览表（v1.0.0）
| 验证码类型                | 是否支持 | 备注说明                  |
|---------------------------|-----------|-----------------------|
| `Turnstile`              | ✅ 支持   | -                     |
| `hCaptcha`               | ❌ 不支持 | 暂未集成                  |
| `ReCaptchaV2`            | 🚧 计划支持 | 当前仅支持 Turnstile 类型验证码 |
| `ReCaptchaV3`            | 🚧 计划支持| 需模拟用户行为，目前未集成         |
| `FunCaptcha`             | ❌ 不支持 | 结构复杂，暂不支持             |
| `Geetest`                | ❌ 不支持 | 无交互组件模拟逻辑             |
| `ImageToText`            | ❌ 不支持 | 本项目不处理纯打码图片           |
| `RotateCaptcha`          | ❌ 不支持 | 需模拟旋转交互，暂不支持          |
| `SlideCaptcha`           | ❌ 不支持 | 缺乏滑动行为模拟              |

## 📦 项目结构

```
.
├── backend/       # FastAPI 服务，提供任务提交、结果查询、WS 任务分发
├── frontend/      # React + Ant Design 前端界面，展示任务状态、节点情况
├── client/        # 基于 Camoufox 的自动化打码客户端（支持多线程+代理）
├── docker-compose.yml
└── README.md
```

---
## 🧠 效果图

![img.png](img.png)

---
## 🚀 快速开始

### 🔧 环境准备

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Nginx（建议部署使用）

---
### 🚀 开箱即用
确保已安装 [Docker](https://www.docker.com/) 和 [Docker Compose](https://docs.docker.com/compose/):

```bash
# 克隆仓库
git clone https://github.com/Brush-Bot/brush-captcha.git
cd brush-captcha
bash install.sh

# 根据提示输入，除了proxy信息为必填信息，其他配置可以直接回车

```
注意：
1、client的基础镜像比较大，建议分开安装
2、请确保运行client端机器能够连接上你的代理ip（科学上网）,建议设置：
```angular2html
IP-CIDR,45.38.0.0/16,proxy,no-resolve
```
```
默认监控页面地址：http://{ip}:8080/
账号：admin
密码：admin
```
### 🚀 单独安装client端
```bash
bash <(curl -sSL https://raw.githubusercontent.com/Brush-Bot/brush-captcha/refs/heads/main/client_install.sh)
```
## 🛠 手动启动

### 🔹 Backend - 后端服务

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

或构建 Docker 镜像运行：

```bash
docker build -t brush-backend ./backend
docker run -d -p 8000:8000 brush-backend
```

---

### 🔹 Frontend - 监控前端
先设置 src/api.js 中的 BASE 值
```bash
cd frontend
npm install
npm run build
# 本地预览
npm install -g serve
serve -s dist -l 3000
```

建议通过nginx反代，未验证brush直接使用http是否可行

---

### 🔹 Client - 分布式打码节点
参考client目录中config.yaml修改对应参数
```bash
cd client
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_client.py  # 或通过 Docker 启动分布式 worker
```

---

## 📄 示例 Nginx 配置

```nginx
server {
    listen 8998 ssl;
    server_name yourdomain;

    ssl_certificate yourpath;
    ssl_certificate_key yourpath;

    location / {
	    root /home/ubuntu/capsolver_server_dashboard/build;
        index index.html;
        try_files $uri /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    location /ws/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 📦 后续计划

- [ ] 多类型验证码支持（Google, hCaptcha）
- [ ] 节点优先级调度策略

---

## 💬 联系与支持

如果你有任何建议或问题，欢迎提交 [Issues](https://github.com/0xC0FFEE42/brush-captcha/issues) 或 PR！

---
