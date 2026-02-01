"""
英语学习辅助应用 - FastAPI主入口

提供RESTful API服务
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print(f"🚀 启动英语学习辅助应用 API 服务")
    print(f"📍 服务地址: http://{settings.app.host}:{settings.app.port}")
    print(f"📚 API文档: http://{settings.app.host}:{settings.app.port}/docs")
    
    yield
    
    # 关闭时执行
    print("\n👋 正在关闭服务...")


# 创建FastAPI应用
app = FastAPI(
    title="英语学习辅助应用 API",
    description="""
    基于AI的英语学习辅助系统
    
    ## 主要功能
    
    - 📚 **教材管理**: 上传、解析和管理英语教材
    - 💬 **智能对话**: 基于教材内容的智能问答
    - 📝 **测试生成**: 自动生成英语测试题目
    - 📊 **学习统计**: 跟踪学习进度和成绩统计
    
    ## 技术栈
    
    - FastAPI + Python
    - Supabase (数据库 + 认证)
    - 阿里云百炼 (通义千问大模型)
    - 阿里云 OSS (文件存储)
    """,
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 导入并注册路由
from app.api import users, textbooks, chat, tests

app.include_router(users.router, prefix="/api/auth", tags=["认证"])
app.include_router(textbooks.router, prefix="/api/textbooks", tags=["教材"])
app.include_router(chat.router, prefix="/api/chat", tags=["对话"])
app.include_router(tests.router, prefix="/api/tests", tags=["测试"])


@app.get("/")
async def root():
    """根路径 - 健康检查"""
    return {
        "status": "ok",
        "message": "英语学习辅助应用 API 服务运行中",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug
    )
