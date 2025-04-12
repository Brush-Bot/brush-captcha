#!/bin/bash

echo "=== Client 安装脚本 ==="

# 获取宿主机 IP
HOST_IP=$(hostname -I | awk '{for(i=1;i<=NF;i++) if ($i != "127.0.0.1") { print $i; exit } }')
read -p "检测到宿主机 IP 为 $HOST_IP，是否使用？[Y/n]: " use_ip
use_ip=${use_ip:-Y}
if [[ "$use_ip" =~ ^[Nn]$ ]]; then
  read -p "请输入宿主机 IP: " HOST_IP
fi

# 用户传参
read -p "请输入 Proxy Server (例如 http://ip:port): " proxy_server
read -p "请输入 Proxy Username: " proxy_username
read -p "请输入 Proxy Password: " proxy_password
read -p "请输入 WSS 服务器地址（支持完整 URL 或仅 IP，默认 $HOST_IP）: " wss_ip
wss_ip=${wss_ip:-$HOST_IP}
read -p "请输入 WSS 服务器端口（默认 8000）: " wss_port
wss_port=${wss_port:-8000}
read -p "请输入 Worker Name (默认 test): " worker_name
worker_name=${worker_name:-test}

# 判断wss还是ws
if [[ "$wss_ip" == *"://"* ]]; then
  final_wss_url="$wss_ip/worker/"
else
  final_wss_url="ws://$wss_ip:$wss_port/worker/"
fi

# 生成 client/config/config.yaml
mkdir -p client/config
cat > client/config/config.yaml <<EOF
concurrency: null

camoufox:
  api_key: "test"
  solver_type:
    - ImageToTextTask
    - AntiTurnstileTaskProxyLess
  headless: "true"

worker:
  name: "$worker_name"
  wss_url: "$final_wss_url"

proxy:
  server: "$proxy_server"
  username: "$proxy_username"
  password: "$proxy_password"
EOF

echo "✅ 已生成 client/config/config.yaml"

# 启动 client 容器
echo "🚀 正在启动 client 容器..."
docker compose up -d client
echo "✅ client 容器已启动"
