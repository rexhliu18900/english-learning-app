# AI英语学习助手 - 部署指南

## 前端部署到 Vercel（免费）

### 步骤 1：推送代码到 GitHub

```bash
cd /Users/yq800830/.minimax-agent-cn/projects/2/english-learning-app

# 给脚本添加执行权限
chmod +x push-to-github.sh

# 运行推送脚本
./push-to-github.sh
```

脚本会要求您输入：
- GitHub 用户名
- 您的名字和邮箱
- 提交信息
- GitHub 密码或 Personal Access Token

### 步骤 2：在 Vercel 部署

1. **访问 Vercel**: https://vercel.com
2. **登录**: 用 GitHub 账号登录
3. **添加项目**: 点击 "Add New Project"
4. **选择仓库**: 选择 `english-learning-app`
5. **配置设置**:
   - Framework Preset: `Vue.js` (自动检测)
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
6. **环境变量** (可选):
   - `VITE_API_BASE_URL`: 后端 API 地址
7. **部署**: 点击 "Deploy"

### 步骤 3：获取访问地址

部署成功后，Vercel 会提供一个访问地址，例如：
```
https://english-learning-app.vercel.app
```

## 后端部署（本地 Mac）

由于后端需要运行在有公网 IP 的服务器上，测试阶段可以：

### 方式 1：本地运行 + 内网穿透（推荐）

1. **启动后端服务**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **安装内网穿透工具**:
   - 下载 ngrok: https://ngrok.com/download
   - 或使用其他内网穿透服务

3. **启动内网穿透**:
```bash
ngrok http 8000
```

4. **获取公网地址**:
   - ngrok 会提供一个临时公网地址，如 `https://abc123.ngrok.io`
   - 将此地址配置到前端的 `VITE_API_BASE_URL` 环境变量

### 方式 2：部署到云服务器（后期）

当需要正式使用时，部署到阿里云 ECS：
- 参考 `DEPLOYMENT.md` 文档
- 预计费用：50-70 元/月

## 架构说明

```
用户浏览器
    ↓ HTTPS
Vercel（前端）- 托管静态页面
    ↓ API 请求
您的 MacBook（后端 + 内网穿透）
    ↓
阿里云 Supabase（数据库）
```

## 免费额度

| 服务 | 免费额度 |
|------|----------|
| Vercel | 100GB 带宽/月 |
| Supabase | 500MB 数据库 |
| 阿里云百炼 | 有免费 token 额度 |

## 费用汇总（测试阶段）

- **前端**: 0 元（Vercel 免费）
- **后端**: 0 元（本地运行）
- **数据库**: 0 元（Supabase 免费）
- **AI API**: 按量付费（阿里云百炼）
- **总计**: 0 元（仅可能产生少量 AI API 费用）

## 注意事项

1. **内网穿透地址是临时的**，每次重启 ngrok 都会变化
2. **测试满意后**，建议购买云服务器获得固定地址
3. **阿里云百炼有免费额度**，日常测试足够使用
4. **随时可以停止**，不产生任何费用

## 常见问题

Q: 推送失败怎么办？
A: 1. 检查 GitHub 仓库是否存在 2. 使用 Personal Access Token 替代密码 3. 检查网络连接

Q: Vercel 部署失败怎么办？
A: 1. 检查 vercel.json 配置 2. 确保前端已构建成功 3. 查看错误日志

Q: 后端 API 无法连接？
A: 1. 确认后端服务已启动 2. 确认内网穿透已连接 3. 检查前端 API 地址配置

## 联系方式

如有问题，请提供：
1. 错误截图
2. 操作步骤
3. 环境信息（macOS 版本等）
