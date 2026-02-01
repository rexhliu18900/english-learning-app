"""
英语学习辅助应用 - 测试管理API路由

提供测试生成、执行、批改、统计等接口
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel
from supabase import create_client, Client

from config import settings
from auth import get_current_user
from database import User, TestRecord, AnswerRecord
from services.test_generator import test_generator
from services.llm_service import llm_service

router = APIRouter()

# Supabase客户端
supabase: Client = create_client(
    settings.supabase.url,
    settings.supabase.service_key
)


# 请求/响应模型
class GenerateTestRequest(BaseModel):
    """生成测试请求"""
    textbook_id: str
    test_type: str = "unit"  # unit, comprehensive
    unit_numbers: Optional[List[int]] = None  # 指定单元列表
    point_types: Optional[List[str]] = None  # vocabulary, grammar, sentence
    difficulty: str = "medium"  # easy, medium, hard
    question_count: Optional[int] = None  # 不指定则自动计算


class QuestionResponse(BaseModel):
    """题目响应"""
    id: str
    type: str
    question: str
    options: Optional[List[str]] = None
    time_limit: Optional[int] = None  # 预计时间（秒）


class SubmitAnswerRequest(BaseModel):
    """提交答案请求"""
    question_id: str
    answer: str
    time_spent: Optional[int] = 0  # 答题耗时（秒）


class SubmitTestRequest(BaseModel):
    """提交测试请求"""
    answers: List[SubmitAnswerRequest]


class TestResultResponse(BaseModel):
    """测试结果响应"""
    test_id: str
    total_questions: int
    correct_count: int
    wrong_count: int
    score: float
    passed: bool
    correct_answers: List[Dict]
    wrong_answers: List[Dict]
    analysis: Dict
    review_test_id: Optional[str] = None


class TestRecordResponse(BaseModel):
    """测试记录响应"""
    id: str
    test_type: str
    test_scope: Dict
    total_questions: int
    correct_count: int
    score: float
    difficulty: str
    status: str
    started_at: str
    completed_at: Optional[str] = None


class StatisticsResponse(BaseModel):
    """统计数据响应"""
    total_tests: int
    total_questions: int
    correct_rate: float
    weak_points: List[Dict]
    learning_progress: List[Dict]


@router.post("/generate")
async def generate_test(
    request: GenerateTestRequest,
    current_user: User = Depends(get_current_user)
):
    """
    生成测试
    
    根据指定范围和参数生成测试题目
    """
    try:
        # 验证教材访问权限
        tb_resp = supabase.table("textbooks").select("user_id, name").eq("id", request.textbook_id).execute()
        
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
        units_resp = supabase.table("units").select("id, unit_number, title").eq("textbook_id", request.textbook_id).execute()
        
        # 筛选指定单元
        if request.unit_numbers:
            unit_ids = [u["id"] for u in units_resp.data or [] if u["unit_number"] in request.unit_numbers]
        else:
            unit_ids = [u["id"] for u in units_resp.data or []]
        
        if not unit_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未找到指定单元"
            )
        
        # 构建查询
        query = supabase.table("knowledge_points").select("*").in_("unit_id", unit_ids)
        
        if request.point_types:
            query = query.in_("point_type", request.point_types)
        
        kp_resp = query.execute()
        knowledge_points = kp_resp.data or []
        
        if not knowledge_points:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未找到相关知识点"
            )
        
        # 生成测试范围描述
        unit_map = {u["id"]: u for u in units_resp.data or []}
        test_scope = {
            "type": request.test_type,
            "textbook_name": tb_resp.data[0]["name"],
            "units": [unit_map[uid]["title"] for uid in unit_ids],
            "point_types": request.point_types or ["vocabulary", "grammar", "sentence"]
        }
        
        # 生成测试
        test = test_generator.generate_test(
            knowledge_points=knowledge_points,
            test_scope=test_scope,
            difficulty=request.difficulty,
            question_count=request.question_count
        )
        
        # 保存测试记录
        test_id = str(uuid4())
        test_record = {
            "id": test_id,
            "user_id": current_user.id,
            "textbook_id": request.textbook_id,
            "test_type": request.test_type,
            "test_scope": test_scope,
            "total_questions": test["total_questions"],
            "correct_count": 0,
            "score": 0,
            "difficulty": request.difficulty,
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("test_records").insert(test_record).execute()
        
        # 保存题目（不包含正确答案）
        questions_for_user = []
        for i, q in enumerate(test["questions"]):
            question_id = str(uuid4())
            
            # 保存完整题目（包含答案）
            question_record = {
                "id": question_id,
                "test_id": test_id,
                "knowledge_point_id": None,  # 可以关联知识点
                "question_type": q["type"],
                "question_content": {
                    "id": question_id,
                    "question": q["question"],
                    "options": q.get("options"),
                    "explanation": q.get("explanation"),
                    "knowledge_point": q.get("knowledge_point")
                },
                "correct_answer": q["answer"],
                "question_difficulty": request.difficulty
            }
            
            supabase.table("answer_records").insert(question_record).execute()
            
            # 返回给用户的题目（不含答案）
            questions_for_user.append({
                "id": question_id,
                "type": q["type"],
                "question": q["question"],
                "options": q.get("options"),
                "time_limit": 120  # 每题约2分钟
            })
        
        return {
            "test_id": test_id,
            "questions": questions_for_user,
            "total_questions": test["total_questions"],
            "time_limit": test["time_limit"],
            "difficulty": request.difficulty
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成测试失败: {str(e)}"
        )


@router.post("/{test_id}/submit", response_model=TestResultResponse)
async def submit_test(
    test_id: str,
    request: SubmitTestRequest,
    current_user: User = Depends(get_current_user)
):
    """
    提交测试答案
    """
    try:
        # 获取测试记录
        test_resp = supabase.table("test_records").select("*").eq("id", test_id).execute()
        
        if not test_resp.data or len(test_resp.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="测试不存在"
            )
        
        test_record = test_resp.data[0]
        
        # 验证权限
        if test_record["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此测试"
            )
        
        # 检查测试状态
        if test_record["status"] == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="测试已提交"
            )
        
        # 获取题目
        questions_resp = supabase.table("answer_records").select("*").eq("test_id", test_id).execute()
        questions = {q["id"]: q for q in questions_resp.data or []}
        
        # 批改
        answers_for_grading = []
        for ans in request.answers:
            if ans.question_id in questions:
                q = questions[ans.question_id]
                correct_answer = q.get("correct_answer", "")
                
                # 标准化答案比较
                user_ans = str(ans.answer).strip().lower()
                correct_ans = str(correct_answer).strip().lower()
                
                is_correct = user_ans == correct_ans
                
                answers_for_grading.append({
                    "question_id": ans.question_id,
                    "question_content": q.get("question_content", {}),
                    "user_answer": ans.answer,
                    "correct_answer": correct_answer,
                    "is_correct": is_correct,
                    "time_spent": ans.time_spent,
                    "knowledge_point": q.get("question_content", {}).get("knowledge_point")
                })
        
        # 调用测试生成器的批改功能
        test = {
            "questions": [{
                "question": a["question_content"].get("question", ""),
                "answer": a["correct_answer"],
                "type": "choice",
                "explanation": a["question_content"].get("explanation", ""),
                "knowledge_point": a["question_content"].get("knowledge_point", "")
            } for a in answers_for_grading]
        }
        
        answers_for_grading_normalized = [{
            "question_id": a["question_content"].get("id", ""),
            "question_content": a["question_content"],
            "user_answer": a["user_answer"],
            "correct_answer": a["correct_answer"],
            "is_correct": a["is_correct"],
            "knowledge_point": a["knowledge_point"]
        } for a in answers_for_grading]
        
        # 计算分数
        correct_count = sum(1 for a in answers_for_grading if a["is_correct"])
        total = len(answers_for_grading)
        score = (correct_count / total * 100) if total > 0 else 0
        passed = score >= 60
        
        # 更新测试记录
        supabase.table("test_records").update({
            "correct_count": correct_count,
            "score": round(score, 2),
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat()
        }).eq("id", test_id).execute()
        
        # 分类正确答案和错误答案
        correct_answers = []
        wrong_answers = []
        
        for a in answers_for_grading:
            if a["is_correct"]:
                correct_answers.append({
                    "question": a["question_content"].get("question", ""),
                    "your_answer": a["user_answer"],
                    "correct_answer": a["correct_answer"],
                    "explanation": a["question_content"].get("explanation", "")
                })
            else:
                wrong_answers.append({
                    "question": a["question_content"].get("question", ""),
                    "question_type": "choice",
                    "your_answer": a["user_answer"],
                    "correct_answer": a["correct_answer"],
                    "explanation": a["question_content"].get("explanation", ""),
                    "knowledge_point": a["knowledge_point"],
                    "question_content": a["question_content"]
                })
        
        # 错题分析
        analysis = {}
        if wrong_answers:
            analysis = llm_service.analyze_errors(wrong_answers, [])
        
        return {
            "test_id": test_id,
            "total_questions": total,
            "correct_count": correct_count,
            "wrong_count": total - correct_count,
            "score": round(score, 2),
            "passed": passed,
            "correct_answers": correct_answers,
            "wrong_answers": wrong_answers,
            "analysis": analysis,
            "review_test_id": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交失败: {str(e)}"
        )


@router.get("/records", response_model=List[TestRecordResponse])
async def get_test_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """
    获取测试记录列表
    """
    try:
        offset = (page - 1) * page_size
        
        response = supabase.table("test_records").select("*").eq("user_id", current_user.id).order("created_at", desc=True).range(offset, offset + page_size - 1).execute()
        
        records = []
        for tr in response.data or []:
            records.append({
                "id": tr["id"],
                "test_type": tr["test_type"],
                "test_scope": tr.get("test_scope", {}),
                "total_questions": tr["total_questions"],
                "correct_count": tr.get("correct_count", 0),
                "score": tr.get("score", 0),
                "difficulty": tr["difficulty"],
                "status": tr["status"],
                "started_at": tr["started_at"],
                "completed_at": tr.get("completed_at")
            })
        
        return records
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取记录失败: {str(e)}"
        )


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    current_user: User = Depends(get_current_user)
):
    """
    获取学习统计
    """
    try:
        # 获取所有测试记录
        test_resp = supabase.table("test_records").select("*").eq("user_id", current_user.id).eq("status", "completed").execute()
        
        tests = test_resp.data or []
        total_tests = len(tests)
        
        if total_tests == 0:
            return {
                "total_tests": 0,
                "total_questions": 0,
                "correct_rate": 0,
                "weak_points": [],
                "learning_progress": []
            }
        
        # 计算总题数和正确率
        total_questions = sum(tr.get("total_questions", 0) for tr in tests)
        total_correct = sum(tr.get("correct_count", 0) for tr in tests)
        correct_rate = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # 分析薄弱知识点
        wrong_kps = {}
        for tr in tests:
            if tr.get("wrong_answers"):
                for wa in tr["wrong_answers"]:
                    kp = wa.get("knowledge_point", "未知")
                    if kp:
                        wrong_kps[kp] = wrong_kps.get(kp, 0) + 1
        
        weak_points = sorted([
            {"knowledge_point": kp, "wrong_count": count}
            for kp, count in wrong_kps.items()
        ], key=lambda x: x["wrong_count"], reverse=True)[:5]
        
        # 学习进度（按月统计）
        progress_by_month = {}
        for tr in tests:
            month = tr.get("completed_at", "")[:7] if tr.get("completed_at") else "未知"
            if month not in progress_by_month:
                progress_by_month[month] = {"tests": 0, "correct_rate": 0, "total_questions": 0}
            progress_by_month[month]["tests"] += 1
            progress_by_month[month]["total_questions"] += tr.get("total_questions", 0)
        
        learning_progress = [
            {"month": month, "tests": data["tests"], "total_questions": data["total_questions"]}
            for month, data in sorted(progress_by_month.items())
        ]
        
        return {
            "total_tests": total_tests,
            "total_questions": total_questions,
            "correct_rate": round(correct_rate, 2),
            "weak_points": weak_points,
            "learning_progress": learning_progress
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计失败: {str(e)}"
        )


@router.post("/review/{wrong_test_id}")
async def generate_review_test(
    wrong_test_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    根据错题生成复习测试
    """
    try:
        # 获取原测试记录
        test_resp = supabase.table("test_records").select("*").eq("id", wrong_test_id).execute()
        
        if not test_resp.data or len(test_resp.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="测试不存在"
            )
        
        test_record = test_resp.data[0]
        
        if test_record["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此测试"
            )
        
        # 获取错题
        wrong_answers = test_record.get("wrong_answers", [])
        
        if not wrong_answers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该测试没有错题"
            )
        
        # 生成复习测试
        review_test = test_generator.generate_wrong_test(
            wrong_answers=wrong_answers,
            knowledge_points=[],
            difficulty="medium"
        )
        
        return {
            "message": "复习测试生成成功",
            "test": review_test
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成复习测试失败: {str(e)}"
        )
