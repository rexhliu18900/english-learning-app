"""
英语学习辅助应用 - 后端服务包
"""

from app.api import router
from app.database import Base, engine

# 初始化数据库表
def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)


__all__ = ["router", "init_db"]
