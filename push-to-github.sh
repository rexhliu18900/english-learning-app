#!/bin/bash

# AI英语学习助手 - Git 推送脚本
# 将项目推送到 GitHub

set -e

# 配置（请修改为您的信息）
GITHUB_USERNAME="您的GitHub用户名"
REPO_NAME="english-learning-app"
BRANCH="main"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Git 推送脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查 Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git 未安装，请先安装 Git${NC}"
    echo "下载: https://git-scm.com/downloads"
    exit 1
fi

echo -e "${GREEN}Git 已安装${NC}"

# 获取当前目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "项目目录: $PROJECT_DIR"
echo ""

# 初始化 Git（如果未初始化）
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}初始化 Git 仓库...${NC}"
    git init
    git checkout -b $BRANCH
else
    echo -e "${GREEN}Git 仓库已存在${NC}"
fi

# 配置用户信息（如果未配置）
if [ -z "$(git config user.name)" ]; then
    echo -e "${YELLOW}请配置 Git 用户信息:${NC}"
    read -p "您的名字: " USER_NAME
    read -p "您的邮箱: " USER_EMAIL
    git config user.name "$USER_NAME"
    git config user.email "$USER_EMAIL"
fi

echo ""
echo -e "${YELLOW}添加文件到 Git...${NC}"
git add .

# 检查是否有文件添加
if git diff --cached --quiet; then
    echo -e "${YELLOW}没有新文件需要提交${NC}"
else
    echo -e "${YELLOW}提交文件...${NC}"
    read -p "提交信息: " COMMIT_MSG
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="Update: $(date '+%Y-%m-%d %H:%M')"
    fi
    git commit -m "$COMMIT_MSG"
fi

# 设置远程仓库
echo ""
echo -e "${YELLOW}设置远程仓库...${NC}"
REMOTE_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

if git remote get-url origin &> /dev/null; then
    echo "远程仓库已配置: $(git remote get-url origin)"
    read -p "是否更新远程仓库地址? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote set-url origin "$REMOTE_URL"
        echo "已更新远程仓库地址"
    fi
else
    git remote add origin "$REMOTE_URL"
    echo "已添加远程仓库: $REMOTE_URL"
fi

# 推送到 GitHub
echo ""
echo -e "${YELLOW}推送到 GitHub...${NC}"
echo -e "${YELLOW}请输入您的 GitHub 密码（或 Personal Access Token）${NC}"

if git push -u origin $BRANCH; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  推送成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "下一步:"
    echo "1. 访问 https://vercel.com"
    echo "2. 用 GitHub 登录"
    echo "3. 点击 'Add New Project'"
    echo "4. 选择 'english-learning-app' 仓库"
    echo "5. 配置:"
    echo "   - Root Directory: frontend"
    echo "   - Build Command: npm run build"
    echo "   - Output Directory: dist"
    echo "6. 点击 Deploy"
    echo ""
    echo -e "${GREEN}部署成功后会获得访问地址！${NC}"
else
    echo ""
    echo -e "${RED}推送失败，可能的原因:${NC}"
    echo "1. 仓库不存在 - 请先在 GitHub 创建仓库"
    echo "2. 权限问题 - 使用 Personal Access Token 替代密码"
    echo "3. 网络问题 - 检查网络连接"
fi
