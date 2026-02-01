#!/bin/bash

# AI英语学习助手 - 系统测试脚本
# 用于验证部署是否成功

set -e

# 配置
API_BASE="http://localhost:8000"
FRONTEND_BASE="http://localhost:80"
API_KEYS_FILE="$HOME/.english-learning-test-keys"

# 测试结果
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
test_passed() {
    echo -e "\033[0;32m✓ $1\033[0m"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

test_failed() {
    echo -e "\033[0;31m✗ $1\033[0m"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

test_info() {
    echo -e "\033[0;34m→ $1\033[0m"
}

# 检查服务状态
test_services() {
    echo ""
    echo "========================================"
    echo "  服务可用性测试"
    echo "========================================"
    
    # 测试后端 API
    test_info "测试后端 API..."
    if curl -s -o /dev/null -w "%{http_code}" "$API_BASE/docs" | grep -q "200"; then
        test_passed "后端 API 可访问"
    else
        test_failed "后端 API 不可访问"
    fi
    
    # 测试前端
    test_info "测试前端页面..."
    if curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_BASE" | grep -q "200"; then
        test_passed "前端页面可访问"
    else
        test_failed "前端页面不可访问"
    fi
}

# 测试 API 接口
test_api() {
    echo ""
    echo "========================================"
    echo "  API 接口测试"
    echo "========================================"
    
    # 测试健康检查
    test_info "测试健康检查接口..."
    if curl -s "$API_BASE/health" | grep -q '"status"'; then
        test_passed "健康检查通过"
    else
        test_failed "健康检查失败"
    fi
    
    # 测试注册
    test_info "测试用户注册..."
    local register_response=$(curl -s -X POST "$API_BASE/api/auth/register" \
        -H "Content-Type: application/json" \
        -d '{"email":"test'"$(date +%s)"'@example.com","password":"test123","name":"测试用户","role":"student"}')
    
    if echo "$register_response" | grep -q '"token"'; then
        test_passed "用户注册成功"
        # 保存 token 用于后续测试
        echo "$register_response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4 > "$API_KEYS_FILE"
    elif echo "$register_response" | grep -q "already exists"; then
        test_passed "用户已存在（正常）"
    else
        test_failed "用户注册失败: $register_response"
    fi
    
    # 测试登录
    test_info "测试用户登录..."
    local login_response=$(curl -s -X POST "$API_BASE/api/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","password":"test123"}')
    
    if echo "$login_response" | grep -q '"token"'; then
        test_passed "用户登录成功"
        echo "$login_response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4 >> "$API_KEYS_FILE"
    else
        test_failed "用户登录失败"
    fi
}

# 测试功能模块
test_modules() {
    echo ""
    echo "========================================"
    echo "  功能模块测试"
    echo "========================================"
    
    # 获取 token
    local token=""
    if [ -f "$API_KEYS_FILE" ]; then
        token=$(head -n 1 "$API_KEYS_FILE")
    fi
    
    if [ -z "$token" ]; then
        test_info "跳过需要认证的测试（无有效 token）"
        return
    fi
    
    # 测试教材列表
    test_info "测试获取教材列表..."
    if curl -s -X GET "$API_BASE/api/textbooks" \
        -H "Authorization: Bearer $token" | grep -q "textbooks\|data"; then
        test_passed "获取教材列表成功"
    else
        test_failed "获取教材列表失败"
    fi
    
    # 测试 AI 对话
    test_info "测试 AI 对话功能..."
    local chat_response=$(curl -s -X POST "$API_BASE/api/chat" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $token" \
        -d '{"message":"什么是现在完成时？"}')
    
    if echo "$chat_response" | grep -q "answer\|message"; then
        test_passed "AI 对话功能正常"
    else
        test_failed "AI 对话功能异常"
    fi
}

# 生成测试报告
generate_report() {
    echo ""
    echo "========================================"
    echo "  测试结果汇总"
    echo "========================================"
    echo ""
    echo -e "通过: \033[0;32m$TESTS_PASSED\033[0m"
    echo -e "失败: \033[0;31m$TESTS_FAILED\033[0m"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\033[0;32m========================================\033[0m"
        echo -e "\033[0;32m  所有测试通过！部署成功！\033[0m"
        echo -e "\033[0;32m========================================\033[0m"
        return 0
    else
        echo -e "\033[0;31m========================================\033[0m"
        echo -e "\033[0;31m  部分测试失败，请检查日志\033[0m"
        echo -e "\033[0;31m========================================\033[0m"
        return 1
    fi
}

# 清理测试数据
cleanup() {
    if [ -f "$API_KEYS_FILE" ]; then
        rm "$API_KEYS_FILE"
    fi
}

# 主函数
main() {
    echo "AI英语学习助手 - 系统测试"
    echo "========================="
    echo ""
    
    # 捕获中断信号
    trap cleanup EXIT
    
    test_services
    test_api
    test_modules
    
    generate_report
}

main "$@"
