# AI 英语学习助手 - 部署指南

## 项目概述

AI 英语学习助手是一款专为初中生设计的智能英语学习应用，支持：
- AI 智能问答（基于教材内容）
- 智能测试生成（选择题、填空题、判断题、阅读理解）
- 错题分析与学习统计
- 家长端功能
- PWA 移动端支持

## 技术栈

- **后端**: Python FastAPI + SQLAlchemy + Supabase
- **前端**: Vue.js 3 + Element Plus + Chart.js
- **AI**: 阿里云通义千问 (Qwen)
- **存储**: 阿里云 OSS + Supabase PostgreSQL
- **部署**: Docker + Nginx

## 前置要求

1. Docker 和 Docker Compose
2. Node.js 18+ (本地开发)
3. Python 3.10+ (本地开发)

## 快速部署

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd english-learning-app
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env
```

填写以下配置：

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# 阿里云百炼 API
ALIBABA_API_KEY=sk-your-api-key

# 阿里云 OSS
OSS_ACCESS_KEY_ID=your-access-key-id
OSS_ACCESS_KEY_SECRET=your-access-key-secret
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=english-learning--judy

# 应用设置
APP_SECRET_KEY=your-secret-key-min-32-chars
```

### 3. 部署到服务器

#### 使用 Docker Compose (推荐)

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 服务说明

- **前端**: http://localhost:80
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

### 4. 配置 Nginx (生产环境)

1. 复制 SSL 证书到 `ssl/` 目录
2. 修改 `nginx.conf` 中的域名
3. 重启 nginx

## 本地开发

### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: .\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build
```

## 数据库设置

### Supabase 控制台操作

1. 创建项目: https://supabase.com
2. 进入 SQL Editor
3. 执行 `backend/schema.sql` 中的建表语句

### 数据库表结构

- `users` - 用户表
- `textbooks` - 教材表
- `units` - 单元表
- `knowledge_points` - 知识点表
- `test_records` - 测试记录表
- `answer_records` - 答题记录表

## API 文档

启动后访问: http://localhost:8000/docs

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/textbooks` | GET/POST | 教材管理 |
| `/api/chat` | POST | AI 问答 |
| `/api/tests/generate` | POST | 生成测试 |
| `/api/tests/submit` | POST | 提交答案 |
| `/api/statistics` | GET | 学习统计 |

## 功能测试

### 1. 用户注册/登录

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456","name":"测试用户","role":"student"}'
```

### 2. AI 问答测试

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message":"什么是现在完成时？"}'
```

### 3. 生成测试

```bash
curl -X POST http://localhost:8000/api/tests/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"textbook_id":1,"test_type":"unit","unit_numbers":[1],"question_count":10}'
```

## 常见问题

### Q: 端口被占用怎么办？
A: 修改 `docker-compose.yml` 中的端口映射

### Q: 数据库连接失败？
A: 检查 `.env` 中的 Supabase 配置是否正确

### Q: AI 接口返回错误？
A: 确认阿里云 API Key 有效且余额充足

### Q: 前端静态资源加载失败？
A: 确保已执行 `npm run build` 并正确配置 nginx

## 监控和维护

### 查看服务状态

```bash
docker-compose ps
```

### 查看日志

```bash
# 所有服务日志
docker-compose logs

# 指定服务日志
docker-compose logs backend
docker-compose logs frontend
```

### 数据备份

Supabase 自动进行数据库备份。如需手动备份：
1. 进入 Supabase 控制台
2. 选择 Timepoint Recovery
3. 选择时间点进行恢复

## 安全建议

1. 生产环境关闭 debug 模式
2. 使用强密码和 HTTPS
3. 定期更新 API Key
4. 限制 CORS  origins
5. 启用防火墙只开放必要端口

## License

MIT License
