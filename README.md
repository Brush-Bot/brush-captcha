# 🧠 brush-captcha - 自建打码平台

本项目基于 Camoufox 指纹伪装方案，包含前端页面、后端 API 服务和分布式打码客户端，支持多实例并发运行。

目前支持打码类型：`Turnstile`、`hCaptcha`，后续将根据项目需要集成更多类型打码。

---

## 📦 版本记录（Release History）

| 版本号 | 日期 | 更新内容 | 备注 |
|--------|------|----------|------|
| v1.1.0 | 2025-04-18 | 1. 使用静态代理打码，由 server 端统一调度<br>2. 增加 server 鉴权机制<br>3. 支持 hCaptcha（Gemini 打码）<br>4. 优化 Turnstile 性能<br>5. 任务调度优化 | 关键功能升级 |
| v1.0.0 | -    | 🎉 首个正式版本发布，仅支持 Turnstile 和动态 IP 打码 | 初始稳定版本 |

---

## ✅ 验证码支持情况一览

| 验证码类型         | 支持状态 | 说明 |
|--------------------|----------|------|
| `Turnstile`        | ✅ 支持  | - |
| `hCaptcha`         | ✅ 支持  | 集成 [QIN2DIM/hcaptcha-challenger](https://github.com/QIN2DIM/hcaptcha-challenger)，需 Gemini API Key（性能待优化） |
| `ReCaptchaV2`      | 🚧 计划支持 | 当前仅支持 Turnstile |
| `ReCaptchaV3`      | 🚧 计划支持 | 需模拟用户行为，未集成 |
| `FunCaptcha`       | ❌ 不支持 | 结构复杂，暂不支持 |
| `Geetest`          | ❌ 不支持 | 无交互组件模拟逻辑 |
| `ImageToText`      | ❌ 不支持 | 不处理纯打码图片 |
| `RotateCaptcha`    | ❌ 不支持 | 需模拟旋转交互 |
| `SlideCaptcha`     | ❌ 不支持 | 缺乏滑动行为模拟 |

---

## 📁 项目结构

```bash
.
├── backend/       # Server：提供鉴权、任务调度与 WebSocket 服务
├── frontend/      # 管理页面：React + Ant Design
├── client/        # 分布式打码客户端（基于 Camoufox）
├── docker-compose.yml
└── README.md
```

---

## 🖼 效果预览

![img.png](img.png)

---

## 🚀 快速开始

### 🔧 环境准备

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Nginx（建议部署 SSL）
- Gemini API Key（如使用 hCaptcha）

---

### 🖥 部署server端与前端页面

```bash
git clone https://github.com/Brush-Bot/brush-captcha.git
cd brush-captcha
```

将以下配置文件放入 `tmp/` 目录：

- `proxies.txt`：代理 IP 列表，一行一条，支持多种格式（包括 user:pass@ip:port）
- `user_keys.txt`：用户 Key 列表，可直接填写 Gemini API Key
- `*.crt / *.key / *.pem`：SSL 证书（支持自动拆分识别）
- `nginx.conf.template / nginx.ssl.template`：Nginx 模板

⚡ 示例自签证书命令：

```bash
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout server.key -out server.crt -days 365 \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=MyCompany/OU=Dev/CN=localhost"
```

执行安装脚本：

```bash
bash install_server_and_frontend.sh
```

---

### 🧑‍💻 部署client端

```bash
cd client
nano config.yaml
```

示例配置：

```yaml
# 并发数设置（可选，不填则自动根据系统资源计算）
concurrency: null

# Camoufox 参数配置
camoufox:
  # 当前设备支持的打码类型，支持的类型server端才会分配任务
  solver_type:
    - HcaptchaCracker
    - AntiTurnstileTaskProxyLess
  # 无头模式，默认打开即可
  headless: "true"

worker:
  # 当前设备名称
  name: "test"
  # 后端api地址，替换ip和port即可;如果没有配置ssl，协议头改成ws；切记不能用127.0.0.1和localhost
  wss_url: "wss://ip:8080/ws/worker/"
```

启动：

```bash
docker compose up -d
```

> 📌 注意事项：
> 1. 镜像较大，首次构建需耐心等待；
> 2. 请确保代理连通性（科学上网）；
> 3. 默认监控地址：http://{ip}:8080（默认账号密码均为 `admin`）

---

## 🛠 手动部署方式（可选）

### 🔹 Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

或使用 Docker：

```bash
docker build -t brush-backend ./backend
docker run -d -p 8000:8000 brush-backend
```

---

### 🔹 Frontend

```bash
cd frontend
npm install
npm run build

# 本地预览（可选）
npm install -g serve
serve -s dist -l 3000
```

> 推荐使用 Nginx 进行反代部署。

---

### 🔹 Client

```bash
cd client
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_client.py
```

---

## 📄 示例 Nginx 配置

```nginx
server {
    listen 8998 ssl;
    server_name yourdomain;

    ssl_certificate     /path/to/server.crt;
    ssl_certificate_key /path/to/server.key;

    location / {
        root /path/to/frontend/dist;
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

## 🧩 后续计划

- [ ] ✅ 支持更多验证码类型（ReCaptcha、FunCaptcha）
- [ ] ⚙️ 引入打码节点优先级调度策略
- [ ] 📈 增加打码成功率统计模块

---

## 💬 联系与支持

如有建议或问题，欢迎提交 [Issues](https://github.com/0xC0FFEE42/brush-captcha/issues) 或 PR 🙌