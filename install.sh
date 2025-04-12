#!/bin/bash
# 全局安装脚本：生成 client/config/config.yaml

echo "=== 全局安装脚本 ==="
echo "请依次输入以下参数："

read -p "请输入 Proxy Server (例如 http://ip:port): " proxy_server
read -p "请输入 Proxy Username: " proxy_username
read -p "请输入 Proxy Password: " proxy_password
read -p "请输入 WSS 服务器 IP (默认 127.0.0.1): " wss_ip
wss_ip=${wss_ip:-127.0.0.1}
read -p "请输入 WSS 服务器地址（支持完整URL或仅IP）(默认 127.0.0.1): " wss_ip
wss_ip=${wss_ip:-127.0.0.1}

read -p "请输入 WSS 服务器端口（默认 80）: " wss_port
wss_port=${wss_port:-80}

# 判断是否传了完整协议头
if [[ "$wss_ip" == *"://"* ]]; then
  final_wss_url="$wss_ip/ws/worker/"
else
  final_wss_url="ws://$wss_ip:$wss_port/ws/worker/"
fi

config_dir="client/config"
config_file="$config_dir/config.yaml"

# 如果目录不存在则创建
mkdir -p "$config_dir"

cat > "$config_file" <<EOF
# 并发数设置（可选，不填则自动根据系统资源）
concurrency: null

# Camoufox 参数配置
camoufox:
  api_key: "test" # 可选，暂时未用
  solver_type:
    - ImageToTextTask
    - AntiTurnstileTaskProxyLess
  headless: "true" # 无头模式,建议开启

# worker信息配置
worker:
  name: "$worker_name"  # worker名
  wss_url: "ws://$wss_ip:$wss_port/ws/worker/"  # server地址

# 动态代理配置（仅测试了 ip2world）
proxy:
  server: "$proxy_server"
  username: "$proxy_username"
  password: "$proxy_password"
EOF

echo "配置文件已生成：$config_file"
# 获取宿主机 IP（非回环地址）
HOST_IP=$(hostname -I | awk '{for(i=1;i<=NF;i++) if ($i != "127.0.0.1") { print $i; exit } }')
read -p "检测到宿主机 IP 为 $HOST_IP，是否使用？[Y/n]: " use_ip
use_ip=${use_ip:-Y}
if [[ "$use_ip" =~ ^[Nn]$ ]]; then
  read -p "请输入宿主机 IP: " HOST_IP
fi

# 设置 BASE_API_URL 并写入 .env 文件
BASE_API_URL="http://$HOST_IP:8000"
echo "BASE_API_URL=$BASE_API_URL" > .env
echo "✅ 已写入 BASE_API_URL=$BASE_API_URL 到 .env 文件"

