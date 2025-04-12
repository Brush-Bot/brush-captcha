#!/bin/bash

services=("frontend" "backend" "client")

check_dependencies() {
    echo "🔍 正在检查 Docker 和 docker-compose ..."

    if ! command -v docker &> /dev/null; then
        echo "❌ 未检测到 Docker"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "🍎 请手动安装 Docker Desktop for macOS："
            open https://www.docker.com/products/docker-desktop/
            exit 1
        elif [ -f /etc/debian_version ]; then
            echo "📦 正在为 Debian/Ubuntu 安装 Docker..."
            sudo apt update && sudo apt install -y docker.io
            sudo systemctl enable docker
            sudo systemctl start docker
        else
            echo "❗ 不支持的系统，请手动安装 Docker"
            exit 1
        fi
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo "❌ 未检测到 docker-compose，正在安装..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
            -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi

    echo "✅ Docker 和 docker-compose 已准备就绪"
}

show_menu() {
    echo "🧰 ========== Docker 管理工具箱 =========="
    echo "1. 安装依赖 (Docker + Compose)"
    echo "2. 启动所有服务"
    echo "3. 停止所有服务"
    echo "4. 重启所有服务"
    echo "5. 启动单个服务"
    echo "6. 停止单个服务"
    echo "7. 重启单个服务"
    echo "8. 查看服务日志"
    echo "9. 退出工具箱"
    echo "=========================================="
    echo -n "请输入编号: "
}

select_service() {
    echo "📦 请选择服务:"
    for i in "${!services[@]}"; do
        echo "$((i+1)). ${services[$i]}"
    done
    echo -n "输入编号: "
    read num
    if [[ "$num" =~ ^[1-9]$ ]] && [ "$num" -le "${#services[@]}" ]; then
        service_name="${services[$((num-1))]}"
    else
        echo "❌ 无效服务编号"
        return 1
    fi
}

while true; do
    show_menu
    read choice

    case $choice in
        1)
            check_dependencies
            ;;
        2)
            docker-compose up -d
            ;;
        3)
            docker-compose down
            ;;
        4)
            docker-compose restart
            ;;
        5)
            select_service && docker-compose up -d "$service_name"
            ;;
        6)
            select_service && docker-compose stop "$service_name"
            ;;
        7)
            select_service && docker-compose restart "$service_name"
            ;;
        8)
            select_service && docker-compose logs -f "$service_name"
            ;;
        9)
            echo "👋 已退出工具箱"
            exit 0
            ;;
        *)
            echo "❌ 无效输入，请输入 1~9 的数字"
            ;;
    esac
    echo ""
done