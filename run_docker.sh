#!/bin/bash

# Docker 启动和管理脚本
# 用法: ./run_docker.sh [命令]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目名称
PROJECT_NAME="crypto-arbitrage-bot"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║     🐳 Crypto Arbitrage Bot - Docker Management           ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi

    print_success "Docker环境检查通过"
}

# 构建镜像
build_image() {
    print_header
    print_info "开始构建Docker镜像..."
    docker-compose build --no-cache
    print_success "Docker镜像构建完成"
}

# 启动容器
start_containers() {
    print_header
    print_info "启动Docker容器..."
    docker-compose up -d
    print_success "容器启动成功"
    print_info "访问地址: http://localhost:5000"
}

# 停止容器
stop_containers() {
    print_header
    print_info "停止Docker容器..."
    docker-compose down
    print_success "容器已停止"
}

# 重启容器
restart_containers() {
    print_header
    print_info "重启Docker容器..."
    docker-compose restart
    print_success "容器已重启"
}

# 查看日志
view_logs() {
    print_header
    print_info "查看容器日志 (Ctrl+C退出)..."
    docker-compose logs -f
}

# 查看状态
view_status() {
    print_header
    print_info "容器状态:"
    docker-compose ps
    echo ""

    print_info "容器健康状态:"
    docker inspect --format='{{.State.Health.Status}}' ${PROJECT_NAME}_1 2>/dev/null || echo "无健康检查信息"
}

# 清理容器和镜像
cleanup() {
    print_header
    print_warning "清理所有容器、镜像和卷..."
    read -p "确认清理? (y/N): " confirm

    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        docker-compose down -v --rmi all
        print_success "清理完成"
    else
        print_info "取消清理"
    fi
}

# 进入容器shell
enter_shell() {
    print_header
    print_info "进入容器Shell (退出输入: exit)..."
    docker-compose exec crypto-arbitrage-bot /bin/bash
}

# 更新容器
update_containers() {
    print_header
    print_info "更新容器到最新版本..."
    docker-compose pull
    docker-compose up -d --force-recreate
    print_success "容器更新完成"
}

# 显示帮助信息
show_help() {
    print_header
    echo "用法: ./run_docker.sh [命令]"
    echo ""
    echo "可用命令:"
    echo "  build       构建Docker镜像"
    echo "  start       启动容器"
    echo "  stop        停止容器"
    echo "  restart     重启容器"
    echo "  logs        查看容器日志"
    echo "  status      查看容器状态"
    echo "  shell       进入容器Shell"
    echo "  cleanup     清理所有容器和镜像"
    echo "  update      更新容器"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  ./run_docker.sh build    # 构建镜像"
    echo "  ./run_docker.sh start    # 启动容器"
    echo "  ./run_docker.sh logs     # 查看日志"
}

# 主函数
main() {
    # 检查Docker环境
    check_docker

    # 处理命令
    case "${1:-help}" in
        build)
            build_image
            ;;
        start)
            start_containers
            ;;
        stop)
            stop_containers
            ;;
        restart)
            restart_containers
            ;;
        logs)
            view_logs
            ;;
        status)
            view_status
            ;;
        shell)
            enter_shell
            ;;
        cleanup)
            cleanup
            ;;
        update)
            update_containers
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
