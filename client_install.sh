#!/bin/bash

echo "=== Client 安装脚本 ==="

# 获取宿主机 IP
if [[ "$OSTYPE" == "darwin"* ]]; then
  HOST_IP=$(ipconfig getifaddr en0)
else
  HOST_IP=$(hostname -I | awk '{for(i=1;i<=NF;i++) if ($i != "127.0.0.1") { print $i; exit } }')

# 用户传参
read -p "请输入 WSS 服务器地址（支持完整 URL 或仅 IP，默认 $HOST_IP）: " wss_ip
read -p "请输入 Worker Name (默认 test): " worker_name
worker_name=${worker_name:-test}

# 判断wss还是ws
if [[ "$wss_ip" == *"://"* ]]; then
  final_wss_url="$wss_ip/worker/"
else
  final_wss_url="ws://$wss_ip/worker/"
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
EOF

echo "✅ 已生成 client/config/config.yaml"

# 启动 client 容器
echo "🚀 正在启动 client 容器..."
docker compose up -d client
echo "✅ client 容器已启动"