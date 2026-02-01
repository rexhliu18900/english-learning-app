"""
英语学习辅助应用 - 智能对话API路由

提供基于教材知识的智能问答接口
"""

import json
from typing import List, Optional, Dict
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from supabase import create_client, Client

from config import settings
from auth import get_current_user
from database import User
from services.llm_service import llm_service

router = APIRouter()

# Supabase客户端
supabase: Client = create_client(
    settings.supabase.url,
    settings.supabase.service_key
)


# 请求/响应模型
class ChatRequest(BaseModel):
    """对话请求"""
    message: str
    textbook_id: Optional[str] = None


class ChatResponse(BaseModel):
    """对话响应"""
    answer: str
    suggested_topics: List[str] = []


class KnowledgeQueryRequest(BaseModel):
    """知识查询请求"""
    query: str
    textbook_id: Optional[str] = None
    unit_id: Optional[str] = None
    point_type: Optional[str] = None  # vocabulary, grammar, sentence


class KnowledgeQueryResponse(BaseModel):
    """知识查询响应"""
    query: str
    results: List[Dict]
    related_topics: List[str] = []


class ExplainRequest(BaseModel):
    """知识点解释请求"""
    knowledge_point_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    智能对话问答
    
    基于教材内容回答用户问题，并推荐关联知识点
    """
    try:
        # 如果指定了教材，获取该教材的知识点
        knowledge_context = ""
        
        if request.textbook_id:
            # 验证教材访问权限
            tb_resp = supabase.table("textbooks").select("user_id").eq("id", request.textbook_id).execute()
            
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
            
            # 获取知识点
            units_resp = supabase.table("units").select("id").eq("textbook_id", request.textbook_id).execute()
            unit_ids = [u["id"] for u in units_resp.data or []]
            
            if unit_ids:
                kp_resp = supabase.table("knowledge_points").select("*").in_("unit_id", unit_ids).limit(50).execute()
                
                # 构建知识上下文
                knowledge_items = []
                for kp in kp_resp.data or []:
                    item = {
                        "type": kp.get("point_type", "vocabulary"),
                        "content": kp.get("content", ""),
                        "meaning": kp.get("chinese_meaning", ""),
                        "collocations": kp.get("collocations", []),
                        "examples": kp.get("examples", [])
                    }
                    knowledge_items.append(item)
                
                knowledge_context = json.dumps(knowledge_items, ensure_ascii=False, indent=2)
        
        # 调用大模型回答
        result = llm_service.answer_question(
            question=request.message,
            knowledge_context=knowledge_context
        )
        
        # 生成推荐话题
        suggested_topics = []
        if request.textbook_id:
            # 根据用户问题推荐相关知识点
            suggested_topics = _generate_suggested_topics(request.message, request.textbook_id)
        
        return {
            "answer": result.get("answer", "抱歉，我无法回答您的问题。"),
            "suggested_topics": suggested_topics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"对话失败: {str(e)}"
        )


@router.post("/query", response_model=KnowledgeQueryResponse)
async def query_knowledge(
    request: KnowledgeQueryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    知识查询
    
    根据关键词查询知识点
    """
    try:
        # 构建查询
        query = supabase.table("knowledge_points").select(
            "id, unit_id, point_type, content, phonetic, part_of_speech, chinese_meaning, collocations, examples"
        )
        
        # 验证教材访问权限
        if request.textbook_id:
            tb_resp = supabase.table("textbooks").select("user_id").eq("id", request.textbook_id).execute()
            
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
            
            # 获取该教材的单元
            units_resp = supabase.table("units").select("id").eq("textbook_id", request.textbook_id).execute()
            unit_ids = [u["id"] for u in units_resp.data or []]
            
            if unit_ids:
                query = query.in_("unit_id", unit_ids)
        
        if request.unit_id:
            query = query.eq("unit_id", request.unit_id)
        
        if request.point_type:
            query = query.eq("point_type", request.point_type)
        
        # 执行查询
        response = query.limit(20).execute()

        # 模糊匹配关键词
        results = []
        for kp in response.data or []:
            # 检查关键词匹配
            content = kp.get("content", "").lower()
            meaning = kp.get("chinese_meaning", "").lower()
            query_words = request.query.lower().split()
            
            match = any(word in content or word in meaning for word in query_words)
            
            if match or not request.query:
                results.append({
                    "id": kp["id"],
                    "type": kp["point_type"],
                    "content": kp["content"],
                    "phonetic": kp.get("phonetic"),
                    "part_of_speech": kp.get("part_of_speech"),
                    "chinese_meaning": kp.get("chinese_meaning"),
                    "collocations": kp.get("collocations", []),
                    "examples": kp.get("examples", [])
                })
        
        # 生成关联话题
        related_topics = _generate_related_topics(request.query, request.textbook_id)
        
        return {
            "query": request.query,
            "results": results,
            "related_topics": related_topics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}"
        )


@router.post("/explain")
async def explain_knowledge(
    request: ExplainRequest,
    current_user: User = Depends(get_current_user)
):
    """
    知识点解释
    
    详细解释指定知识点的用法
    """
    try:
        # 获取知识点
        kp_resp = supabase.table("knowledge_points").select(
            "*, units:textbook_id(title)"
        ).eq("id", request.knowledge_point_id).execute()
        
        if not kp_resp.data or len(kp_resp.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识点不存在"
            )
        
        kp = kp_resp.data[0]
        
        # 调用大模型解释
        explanation = llm_service.explain_knowledge_point(kp)
        
        return {
            "knowledge_point": {
                "id": kp["id"],
                "type": kp["point_type"],
                "content": kp["content"],
                "phonetic": kp.get("phonetic"),
                "part_of_speech": kp.get("part_of_speech"),
                "chinese_meaning": kp.get("chinese_meaning"),
                "unit_name": kp.get("units", {}).get("title", "")
            },
            "explanation": explanation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解释失败: {str(e)}"
        )


@router.get("/history")
async def get_chat_history(
    limit: int = Query(default=20, le=100),
    current_user: User = Depends(get_current_user)
):
    """
    获取对话历史
    """
    # TODO: 实现对话历史存储和查询
    return {
        "messages": [],
        "message": "对话历史功能开发中"
    }


def _generate_suggested_topics(message: str, textbook_id: str) -> List[str]:
    """根据用户消息生成推荐话题"""
    suggested = []
    
    # 简单的关键词匹配
    message_lower = message.lower()
    
    if "vocabulary" in message_lower or "单词" in message_lower or "词" in message_lower:
        suggested = ["词汇学习", "词组搭配", "词汇测试"]
    elif "grammar" in message_lower or "语法" in message_lower:
        suggested = ["语法讲解", "语法练习", "句型结构"]
    elif "sentence" in message_lower or "句型" in message_lower or "句子" in message_lower:
        suggested = ["重点句型", "句型练习", "造句练习"]
    elif "test" in message_lower or "测试" in message_lower or "练习" in message_lower:
        suggested = ["综合测试", "单元测试", "词汇测试"]
    else:
        suggested = ["知识点复习", "语法巩固", "阅读理解"]
    
    return suggested


def _generate_related_topics(query: str, textbook_id: str) -> List[str]:
    """生成关联话题"""
    if not query:
        return ["词汇", "语法", "句型", "阅读", "写作"]
    
    query_lower = query.lower()
    related = []
    
    if "unit" in query_lower or "第" in query:
        related = ["本单元词汇", "本单元语法", "综合练习"]
    elif any(word in query_lower for word in ["what", "how", "why", "什么", "如何", "为什么"]):
        related = ["语法解释", "用法说明", "例句展示"]
    elif any(word in query_lower for word in ["difference", "区别", "不同"]):
        related = ["易混淆词", "用法对比", "词汇辨析"]
    else:
        related = ["相关词汇", "扩展知识", "练习巩固"]
    
    return related
