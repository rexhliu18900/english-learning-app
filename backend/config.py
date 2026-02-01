"""
英语学习辅助应用 - 配置管理模块

从环境变量和配置文件加载应用配置
"""

import os
from pathlib import Path
from typing import Optional
from functools import lru_cache

import yaml
from pydantic import BaseModel, Field


class SupabaseConfig(BaseModel):
    """Supabase配置"""
    url: str = Field(..., description="Supabase项目URL")
    anon_key: str = Field(..., description="anon公开密钥")
    service_key: str = Field(..., description="service_role密钥")


class DashScopeConfig(BaseModel):
    """阿里云百炼配置"""
    api_key: str = Field(..., description="API Key")
    base_url: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1")


class OSSConfig(BaseModel):
    """阿里云OSS配置"""
    bucket_name: str = Field(..., description="Bucket名称")
    region: str = Field(..., description="地域节点")
    endpoint: str = Field(..., description="访问域名")
    access_key_id: str = Field(..., description="AccessKey ID")
    access_key_secret: str = Field(..., description="AccessKey Secret")


class AppConfig(BaseModel):
    """应用配置"""
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=False)
    secret_key: str = Field(..., description="JWT密钥")


class Settings(BaseModel):
    """应用设置"""
    supabase: SupabaseConfig
    dashscope: DashScopeConfig
    oss: OSSConfig
    app: AppConfig


def load_config(config_path: Optional[str] = None) -> Settings:
    """加载配置文件"""
    
    # 默认配置文件路径
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.yaml"
    
    # 检查配置文件是否存在
    if not Path(config_path).exists():
        # 如果配置文件不存在，从环境变量加载
        return Settings(
            supabase=SupabaseConfig(
                url=os.getenv("SUPABASE_URL", ""),
                anon_key=os.getenv("SUPABASE_ANON_KEY", ""),
                service_key=os.getenv("SUPABASE_SERVICE_KEY", "")
            ),
            dashscope=DashScopeConfig(
                api_key=os.getenv("DASHSCOPE_API_KEY", ""),
                base_url=os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
            ),
            oss=OSSConfig(
                bucket_name=os.getenv("OSS_BUCKET_NAME", ""),
                region=os.getenv("OSS_REGION", ""),
                endpoint=os.getenv("OSS_ENDPOINT", ""),
                access_key_id=os.getenv("OSS_ACCESS_KEY_ID", ""),
                access_key_secret=os.getenv("OSS_ACCESS_KEY_SECRET", "")
            ),
            app=AppConfig(
                host=os.getenv("APP_HOST", "0.0.0.0"),
                port=int(os.getenv("APP_PORT", "8000")),
                debug=os.getenv("DEBUG", "False").lower() == "true",
                secret_key=os.getenv("SECRET_KEY", "default-secret-key")
            )
        )
    
    # 从YAML文件加载配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    
    return Settings(**config_data)


@lru_cache()
def get_settings() -> Settings:
    """获取应用设置（单例模式）"""
    return load_config()


# 创建全局设置实例
settings = get_settings()
