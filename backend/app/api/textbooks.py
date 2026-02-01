"""
英语学习辅助应用 - 教材管理API路由

提供教材上传、解析、知识查询等接口
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, status
from pydantic import BaseModel
from supabase import create_client, Client

from config import settings
from auth import get_current_user
from database import User, Textbook, Unit, KnowledgePoint
from services.document_parser import DocumentParser

router = APIRouter()

# Supabase客户端
supabase: Client = create_client(
    settings.supabase.url,
    settings.supabase.service_key
)


# 请求/响应模型
class TextbookListResponse(BaseModel):
    """教材列表响应"""
    id: str
    name: str
    version: Optional[str] = None
    file_type: str
    parse_status: str
    statistics: Optional[dict] = None
    created_at: str


class TextbookDetailResponse(BaseModel):
    """教材详情响应"""
    id: str
    name: str
    version: Optional[str] = None
    file_type: str
    parse_status: str
    statistics: Optional[dict] = None
    units: List[dict]
    created_at: str


class KnowledgePointResponse(BaseModel):
    """知识点响应"""
    id: str
    unit_id: str
    unit_name: str
    point_type: str
    content: str
    phonetic: Optional[str] = None
    part_of_speech: Optional[str] = None
    chinese_meaning: Optional[str] = None
    collocations: Optional[List[str]] = None
    examples: Optional[List[str]] = None


class ParseRequest(BaseModel):
    """解析请求"""
    unit_numbers: Optional[List[int]] = None  # 指定解析哪些单元，不指定则解析全部


@router.post("/upload", response_model=dict)
async def upload_textbook(
    file: UploadFile = File(...),
    name: str = Form(...),
    version: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    上传教材文件
    
    支持PDF、Word、PPT格式
    """
    # 检查文件类型
    allowed_types = ['.pdf', '.docx', '.doc', '.md']
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f不支持的文件格式。允许的格式: {', '.join(allowed_types)}"
        )
    
    try:
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        file_name = f"{file_id}{file_ext}"
        
        # 保存文件到本地临时目录
        upload_dir = Path(__file__).parent.parent.parent / "uploads"
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / file_name
        
        # 写入文件
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # 创建教材记录
        textbook_data = {
            "id": file_id,
            "user_id": current_user.id,
            "name": name,
            "version": version,
            "file_type": file_ext[1:],  # 去掉点
            "file_path": str(file_path),
            "parse_status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("textbooks").insert(textbook_data).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="教材创建失败"
            )
        
        return {
            "success": True,
            "message": "教材上传成功",
            "textbook": response.data[0]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败: {str(e)}"
        )


@router.post("/{textbook_id}/parse")
async def parse_textbook(
    textbook_id: str,
    request: ParseRequest = None,
    current_user: User = Depends(get_current_user)
):
    """
    解析教材
    
    解析教材文件，提取知识点
    """
    try:
        # 获取教材信息
        response = supabase.table("textbooks").select("*").eq("id", textbook_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="教材不存在"
            )
        
        textbook = response.data[0]
        
        # 检查权限
        if textbook["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此教材"
            )
        
        # 更新状态为解析中
        supabase.table("textbooks").update({
            "parse_status": "processing",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", textbook_id).execute()
        
        # 解析文档
        file_path = textbook["file_path"]
        parse_result = DocumentParser.parse(file_path)
        
        if not parse_result["success"]:
            # 解析失败
            supabase.table("textbooks").update({
                "parse_status": "failed",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", textbook_id).execute()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"解析失败: {parse_result.get('error', '未知错误')}"
            )
        
        # 保存知识点到数据库
        knowledge_points = parse_result["knowledge_points"]
        units_data = {}
        
        for kp in knowledge_points:
            unit_name = kp.get("unit", "Unknown")
            unit_key = f"{textbook_id}_{unit_name}"
            
            # 获取或创建单元
            if unit_key not in units_data:
                # 检查单元是否已存在
                unit_resp = supabase.table("units").select("id").eq("textbook_id", textbook_id).eq("title", unit_name).execute()
                
                if unit_resp.data and len(unit_resp.data) > 0:
                    unit_id = unit_resp.data[0]["id"]
                else:
                    # 创建新单元
                    unit_resp = supabase.table("units").insert({
                        "textbook_id": textbook_id,
                        "unit_number": len(units_data) + 1,
                        "title": unit_name,
                        "page_range": kp.get("page"),
                        "created_at": datetime.utcnow().isoformat()
                    }).execute()
                    
                    if unit_resp.data and len(unit_resp.data) > 0:
                        unit_id = unit_resp.data[0]["id"]
                    else:
                        continue
                
                units_data[unit_key] = unit_id
            
            # 保存知识点
            kp_data = {
                "id": str(uuid.uuid4()),
                "unit_id": units_data[unit_key],
                "point_type": kp.get("type", "vocabulary"),
                "content": kp.get("content", ""),
                "phonetic": kp.get("phonetic"),
                "part_of_speech": kp.get("part_of_speech"),
                "chinese_meaning": kp.get("chinese_meaning"),
                "collocations": kp.get("collocations", []),
                "examples": kp.get("examples", []),
                "image_description": kp.get("image_description"),
                "created_at": datetime.utcnow().isoformat()
            }
            
            supabase.table("knowledge_points").insert(kp_data).execute()
        
        # 更新教材状态和统计
        statistics = parse_result.get("statistics", {})
        supabase.table("textbooks").update({
            "parse_status": "completed",
            "statistics": statistics,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", textbook_id).execute()
        
        return {
            "success": True,
            "message": "教材解析成功",
            "statistics": statistics,
            "knowledge_points_count": len(knowledge_points)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        supabase.table("textbooks").update({
            "parse_status": "failed",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", textbook_id).execute()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解析失败: {str(e)}"
        )


@router.get("", response_model=List[TextbookListResponse])
async def list_textbooks(
    current_user: User = Depends(get_current_user)
):
    """
    获取教材列表
    """
    try:
        response = supabase.table("textbooks").select("*").eq("user_id", current_user.id).order("created_at", desc=True).execute()
        
        textbooks = []
        for tb in response.data or []:
            textbooks.append({
                "id": tb["id"],
                "name": tb["name"],
                "version": tb.get("version"),
                "file_type": tb["file_type"],
                "parse_status": tb["parse_status"],
                "statistics": tb.get("statistics"),
                "created_at": tb["created_at"]
            })
        
        return textbooks
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取教材列表失败: {str(e)}"
        )


@router.get("/{textbook_id}", response_model=TextbookDetailResponse)
async def get_textbook(
    textbook_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取教材详情
    """
    try:
        # 获取教材
        response = supabase.table("textbooks").select("*").eq("id", textbook_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="教材不存在"
            )
        
        textbook = response.data[0]
        
        # 检查权限
        if textbook["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此教材"
            )
        
        # 获取单元列表
        units_resp = supabase.table("units").select("*").eq("textbook_id", textbook_id).order("unit_number").execute()
        units = []
        
        for unit in units_resp.data or []:
            # 获取该单元的知识点统计
            kp_resp = supabase.table("knowledge_points").select("point_type", count="exact").eq("unit_id", unit["id"]).execute()
            
            vocab_count = 0
            grammar_count = 0
            sentence_count = 0
            
            for kp in kp_resp.data or []:
                if kp.get("point_type") == "vocabulary":
                    vocab_count += 1
                elif kp.get("point_type") == "grammar":
                    grammar_count += 1
                elif kp.get("point_type") == "sentence":
                    sentence_count += 1
            
            units.append({
                "id": unit["id"],
                "unit_number": unit["unit_number"],
                "title": unit["title"],
                "vocabulary_count": vocab_count,
                "grammar_count": grammar_count,
                "sentence_count": sentence_count
            })
        
        return {
            "id": textbook["id"],
            "name": textbook["name"],
            "version": textbook.get("version"),
            "file_type": textbook["file_type"],
            "parse_status": textbook["parse_status"],
            "statistics": textbook.get("statistics"),
            "units": units,
            "created_at": textbook["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取教材详情失败: {str(e)}"
        )


@router.delete("/{textbook_id}")
async def delete_textbook(
    textbook_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    删除教材
    """
    try:
        # 获取教材
        response = supabase.table("textbooks").select("*").eq("id", textbook_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="教材不存在"
            )
        
        textbook = response.data[0]
        
        # 检查权限
        if textbook["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此教材"
            )
        
        # 删除文件
        file_path = textbook.get("file_path")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        # 删除数据库记录（级联删除会自动删除关联的单元和知识点）
        supabase.table("textbooks").delete().eq("id", textbook_id).execute()
        
        return {
            "success": True,
            "message": "教材删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}"
        )


@router.get("/{textbook_id}/knowledge", response_model=List[KnowledgePointResponse])
async def get_knowledge_points(
    textbook_id: str,
    unit_id: Optional[str] = None,
    point_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user)
):
    """
    获取知识点列表
    """
    try:
        # 验证教材访问权限
        tb_resp = supabase.table("textbooks").select("user_id").eq("id", textbook_id).execute()
        
        if not tb_resp.data or len(tb_resp.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="教材不存在"
            )
        
        if tb_resp.data[0]["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此教材"
            )
        
        # 构建查询
        query = supabase.table("knowledge_points").select(
            "id, unit_id, point_type, content, phonetic, part_of_speech, chinese_meaning, collocations, examples"
        )
        
        # 如果指定了单元ID
        if unit_id:
            query = query.eq("unit_id", unit_id)
        else:
            # 获取该教材所有单元
            units_resp = supabase.table("units").select("id").eq("textbook_id", textbook_id).execute()
            unit_ids = [u["id"] for u in units_resp.data or []]
            
            if unit_ids:
                query = query.in_("unit_id", unit_ids)
        
        # 如果指定了知识点类型
        if point_type:
            query = query.eq("point_type", point_type)
        
        # 分页
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        
        response = query.execute()
        
        # 获取单元信息
        units_resp = supabase.table("units").select("id, title").eq("textbook_id", textbook_id).execute()
        unit_map = {u["id"]: u["title"] for u in units_resp.data or []}
        
        # 构建响应
        knowledge_points = []
        for kp in response.data or []:
            knowledge_points.append({
                "id": kp["id"],
                "unit_id": kp["unit_id"],
                "unit_name": unit_map.get(kp["unit_id"], "Unknown"),
                "point_type": kp["point_type"],
                "content": kp["content"],
                "phonetic": kp.get("phonetic"),
                "part_of_speech": kp.get("part_of_speech"),
                "chinese_meaning": kp.get("chinese_meaning"),
                "collations": kp.get("collocations"),
                "examples": kp.get("examples")
            })
        
        return knowledge_points
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识点失败: {str(e)}"
        )
