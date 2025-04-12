#!/bin/bash

echo "=== 一键初始化安装脚本 ==="

HOST_IP=$(hostname -I | awk '{for(i=1;i<=NF;i++) if ($i != "127.0.0.1") { print $i; exit } }')
read -p "检测到宿主机 IP 为 $HOST_IP，是否使用？[Y/n]: " use_ip
use_ip=${use_ip:-Y}
if [[ "$use_ip" =~ ^[Nn]$ ]]; then
  read -p "请输入宿主机 IP: " HOST_IP
fi
BASE_API_URL="http://$HOST_IP:8000"
echo "BASE_API_URL=$BASE_API_URL" > .env
echo "✅ 已写入 .env：BASE_API_URL=$BASE_API_URL"
echo "REACT_APP_BASE_API_URL=$BASE_API_URL" >> .env
echo "✅ 已写入 .env：REACT_APP_BASE_API_URL=$BASE_API_URL"
# 替换nginx
cp frontend/nginx.conf.template frontend/nginx.conf
sed -i "s|__HOST_IP__|$HOST_IP|g" frontend/nginx.conf
echo "✅ 已生成 nginx.conf"

# 用户传参
echo "📌 请输入代理服务器信息，目前仅适配了ip2world，其他请自行适配"
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

# 启动容器
echo "🚀 正在启动容器..."
docker compose up -d

echo "✅ 容器启动完成！"

# 打印访问地址
echo
echo "🌐 访问地址如下："
echo "🔹 前端页面：http://$HOST_IP:8080"
echo "🔹 后端 API：http://$HOST_IP:8000"
echo "🔹 WebSocket 地址：$final_wss_url"
echo


