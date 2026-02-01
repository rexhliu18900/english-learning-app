# 英语学习辅助应用 - 后端服务

## 项目说明
基于FastAPI构建的后端API服务，提供用户认证、教材解析、智能对话、测试生成等功能。

## 技术栈
- FastAPI: 高性能异步Web框架
- Supabase: 数据库和用户认证
- 阿里云百炼: 通义千问大模型API
- 阿里云OSS: 文件存储服务

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
复制 `.env.example` 为 `.env`，并填写配置信息：
```bash
cp .env.example .env
```

### 3. 启动服务
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问API文档
打开浏览器访问：http://localhost:8000/docs

## 项目结构
```
backend/
├── main.py              # 应用入口
├── config.py            # 配置管理
├── requirements.txt     # Python依赖
├── .env                 # 环境变量（不提交到仓库）
├── app/
│   ├── __init__.py
│   ├── config.py        # 配置加载
│   ├── database.py      # 数据库模型
│   ├── auth.py          # 认证逻辑
│   └── api/             # API路由
│       ├── __init__.py
│       ├── users.py     # 用户相关API
│       ├── textbooks.py # 教材相关API
│       ├── chat.py      # 对话相关API
│       └── tests.py     # 测试相关API
└── services/            # 业务逻辑服务
    ├── __init__.py
    ├── document_parser.py  # 文档解析服务
    ├── llm_service.py      # 大模型服务
    └── test_generator.py   # 测试生成服务
```

## API端点

### 用户认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 教材管理
- `POST /api/textbooks/upload` - 上传教材文件
- `GET /api/textbooks` - 获取教材列表
- `GET /api/textbooks/{id}` - 获取教材详情
- `DELETE /api/textbooks/{id}` - 删除教材

### 知识查询
- `POST /api/chat` - 智能对话问答
- `GET /api/knowledge/{textbook_id}` - 获取知识点列表

### 测试管理
- `POST /api/tests/generate` - 生成测试
- `GET /api/tests` - 获取测试记录
- `GET /api/tests/{id}` - 获取测试详情
- `POST /api/tests/{id}/submit` - 提交测试答案

## 许可证
MIT
