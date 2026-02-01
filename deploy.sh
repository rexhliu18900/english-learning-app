#!/bin/bash

# AI英语学习助手 - 一键部署脚本
# 支持本地开发和生产环境部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="AI英语学习助手"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$PROJECT_DIR/.env"

# 打印函数
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  $PROJECT_NAME${NC}"
    echo -e "${BLUE}  一键部署脚本${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_step() {
    echo -e "${YELLOW}步骤 $1: $2${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# 检查环境
check_environment() {
    print_header
    print_step "1" "检查部署环境"
    
    local missing_deps=()
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装"
        missing_deps+=("docker")
    else
        print_success "Docker 已安装 ($(docker --version))"
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装"
        missing_deps+=("docker-compose")
    else
        print_success "Docker Compose 已安装"
    fi
    
    # 检查 Git
    if ! command -v git &> /dev/null; then
        print_error "Git 未安装"
        missing_deps+=("git")
    else
        print_success "Git 已安装 ($(git --version))"
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo ""
        print_error "缺少以下依赖: ${missing_deps[*]}"
        echo "请先安装这些依赖后再运行此脚本"
        exit 1
    fi
    
    echo ""
}

# 检查配置
check_config() {
    print_step "2" "检查配置文件"
    
    if [ ! -f "$ENV_FILE" ]; then
        print_info "未找到 .env 文件，正在创建..."
        cp "$PROJECT_DIR/.env.example" "$ENV_FILE"
        
        echo ""
        print_info "请编辑 $ENV_FILE 填入您的配置"
        echo ""
        echo "需要配置的内容:"
        echo "  1. Supabase URL 和 API Key"
        echo "  2. 阿里云百炼 API Key"
        echo "  3. 阿里云 OSS 认证信息"
        echo "  4. 应用密钥"
        echo ""
        
        # 提示用户编辑配置
        if command -v nano &> /dev/null; then
            read -p "是否现在编辑配置文件? (y/n) " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                nano "$ENV_FILE"
            fi
        fi
    else
        print_success "配置文件已存在"
    fi
    
    # 验证关键配置
    if grep -q "your-project.supabase.co" "$ENV_FILE" 2>/dev/null; then
        print_error "请配置 Supabase 连接信息"
        exit 1
    fi
    
    if grep -q "sk-your-api-key" "$ENV_FILE" 2>/dev/null; then
        print_error "请配置阿里云百炼 API Key"
        exit 1
    fi
    
    echo ""
}

# 构建和部署
deploy() {
    print_step "3" "构建并启动服务"
    
    cd "$PROJECT_DIR"
    
    echo "正在构建 Docker 镜像..."
    if docker-compose up -d --build; then
        print_success "服务启动成功"
    else
        print_error "服务启动失败"
        exit 1
    fi
    
    echo ""
}

# 等待服务就绪
wait_for_services() {
    print_step "4" "等待服务就绪"
    
    local max_attempts=30
    local attempt=0
    
    echo "检查后端服务..."
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:8000/docs &> /dev/null; then
            print_success "后端服务已就绪 (http://localhost:8000)"
            break
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "后端服务启动超时"
        echo ""
        echo "请检查日志: docker-compose logs backend"
    fi
    
    echo ""
}

# 显示部署结果
show_result() {
    print_step "5" "部署完成"
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  部署成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "访问地址:"
    echo -e "  ${BLUE}前端应用:${NC}  http://localhost:80"
    echo -e "  ${BLUE}API 文档:${NC}  http://localhost:8000/docs"
    echo ""
    echo "常用命令:"
    echo "  查看日志:  docker-compose logs -f"
    echo "  重启服务:  docker-compose restart"
    echo "  停止服务:  docker-compose down"
    echo "  更新部署:  git pull && docker-compose up -d --build"
    echo ""
}

# 停止服务
stop_services() {
    print_step "停止服务"
    
    cd "$PROJECT_DIR"
    docker-compose down
    print_success "服务已停止"
}

# 查看状态
show_status() {
    cd "$PROJECT_DIR"
    docker-compose ps
}

# 查看日志
show_logs() {
    cd "$PROJECT_DIR"
    docker-compose logs -f "${1:-}"
}

# 主函数
main() {
    local command=${1:-deploy}
    
    case $command in
        deploy)
            check_environment
            check_config
            deploy
            wait_for_services
            show_result
            ;;
        stop)
            stop_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "${2:-}"
            ;;
        restart)
            stop_services
            sleep 2
            deploy
            wait_for_services
            show_result
            ;;
        help|--help|-h)
            echo "用法: $0 [命令]"
            echo ""
            echo "命令:"
            echo "  deploy   部署应用 (默认)"
            echo "  stop     停止服务"
            echo "  restart  重启服务"
            echo "  status   查看服务状态"
            echo "  logs     查看日志"
echo "  help     显示帮助"
            ;;
        *)
            print_error "未知命令: $command"
            echo "使用 $0 help 查看帮助"
            exit 1
            ;;
    esac
}

main "$@"
