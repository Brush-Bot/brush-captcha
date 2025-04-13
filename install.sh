#!/bin/bash

echo "=== 一键初始化安装脚本 ==="
sedi() {
  if [[ "$(uname)" == "Darwin" ]]; then
    sed -i "" "$@"
  else
    sed -i "$@"
  fi
}
echo "📁 检查并复制代理文件：tmp/proxies.txt → backend/proxy/proxies.txt"
if [[ -f tmp/proxies.txt ]]; then
  mkdir -p backend/proxy
  cp tmp/proxies.txt backend/proxy/proxies.txt
  echo "✅ 已复制 proxies.txt"
else
  echo "❌ 未找到 tmp/proxies.txt，请先准备代理列表！"
  exit 1
fi

BASE_API_URL="http://backend:8000"
SSL_MODE="off"

# 是否使用 SSL
read -p "是否启用 SSL？[y/N]: " use_ssl
use_ssl=${use_ssl:-N}
if [[ "$use_ssl" =~ ^[Yy]$ ]]; then
  echo "🔐 默认从 tmp/ssl.crt 和 tmp/ssl.key 读取证书文件..."
  ssl_crt_path="./tmp/ssl.crt"
  ssl_key_path="./tmp/ssl.key"
  if [[ ! -f "$ssl_crt_path" || ! -f "$ssl_key_path" ]]; then
    echo "❌ 未找到 SSL 证书或密钥文件：$ssl_crt_path / $ssl_key_path"
    exit 1
  fi
  mkdir -p frontend/ssl
  cp "$ssl_crt_path" frontend/ssl/server.crt
  cp "$ssl_key_path" frontend/ssl/server.key
  echo "✅ 已复制 SSL 证书到 frontend/ssl/"

  BASE_API_URL="https://backend:8000"
  SSL_MODE="on"
else
  BASE_API_URL="http://backend:8000"
  SSL_MODE="off"
fi

# 写入 .env
echo "BASE_API_URL=$BASE_API_URL" > .env
echo "DOCKER_API_URL=http://backend:8000" >> .env
echo "✅ 已写入 .env"

# 替换 nginx.conf
if [[ "$SSL_MODE" == "on" ]]; then
  nginx_template="tmp/nginx.ssl.template"
else
  nginx_template="tmp/nginx.conf.template"
fi
if [[ ! -f "$nginx_template" ]]; then
  echo "❌ 找不到 nginx 模板文件: $nginx_template"
  exit 1
fi
cp "$nginx_template" frontend/nginx.conf
sedi "s|__HOST_IP__|backend|g" frontend/nginx.conf
sedi "s|__USE_SSL__|$SSL_MODE|g" frontend/nginx.conf
if [[ "$SSL_MODE" == "on" ]]; then
  sedi "s|__SSL_CRT__|$ssl_crt|g" frontend/nginx.conf
  sedi "s|__SSL_KEY__|$ssl_key|g" frontend/nginx.conf
fi
if grep -q '__HOST_IP__' frontend/nginx.conf; then
  echo "❌ 替换失败：nginx.conf 中仍包含 __HOST_IP__ 占位符。"
  exit 1
fi
echo "✅ 已生成 nginx.conf"

# 用户输入代理配置
read -p "请输入 Worker Name (默认 test): " worker_name
worker_name=${worker_name:-test}

# 容器内访问地址
if [[ "$SSL_MODE" == "on" ]]; then
  final_wss_url="wss://backend:8000/worker/"
else
  final_wss_url="ws://backend:8000/worker/"
fi

# 生成 config.yaml
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

# 清理旧容器 + 镜像
#echo "🧹 清理旧容器和镜像..."
#docker compose --env-file .env down --remove-orphans
#docker image prune -f

# 创建 brush-net 网络（如不存在）
docker network inspect brush-net >/dev/null 2>&1 || docker network create brush-net

# 启动容器（刷上网络）
echo "🚀 正在启动容器..."
docker compose --env-file .env up -d --remove-orphans

echo "✅ 容器启动完成！"

# 提示信息
echo
echo "🌐 访问地址：ip:8080"
echo "🔹 WebSocket 地址：ip:8080"
echo