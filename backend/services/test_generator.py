"""
英语学习辅助应用 - 测试生成服务

根据知识点自动生成测试题目
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from services.llm_service import llm_service
from config import settings


class TestGenerator:
    """测试生成器"""
    
    def __init__(self):
        self.llm = llm_service
    
    def generate_test(self,
                     knowledge_points: List[Dict],
                     test_scope: Dict,
                     difficulty: str = "medium",
                     question_count: Optional[int] = None) -> Dict[str, Any]:
        """
        生成测试
        
        Args:
            knowledge_points: 知识点列表
            test_scope: 测试范围描述
            difficulty: 难度等级
            question_count: 题目数量，如果不指定则自动计算
        
        Returns:
            测试结果
        """
        # 计算题目数量（如果未指定）
        if question_count is None:
            question_count = self._calculate_question_count(knowledge_points)
        
        # 确定题目类型分布
        question_types = self._determine_question_types(knowledge_points)
        
        # 调用大模型生成题目
        questions = self.llm.generate_questions(
            knowledge_points=knowledge_points,
            question_types=question_types,
            difficulty=difficulty,
            count=question_count
        )
        
        if not questions:
            # 如果大模型生成失败，使用简单规则生成备用题目
            questions = self._generate_backup_questions(
                knowledge_points, question_types, question_count
            )
        
        # 计算总分和及格线
        total_score = len(questions)
        passing_score = total_score * 0.6  # 60%及格
        
        return {
            "test_id": str(uuid4()),
            "test_scope": test_scope,
            "questions": questions,
            "total_questions": len(questions),
            "total_score": total_score,
            "passing_score": passing_score,
            "difficulty": difficulty,
            "generated_at": datetime.utcnow().isoformat(),
            "time_limit": self._calculate_time_limit(len(questions))
        }
    
    def _calculate_question_count(self, knowledge_points: List[Dict]) -> int:
        """根据知识点数量计算题目数量"""
        count = len(knowledge_points)
        
        # 自动计算：每个知识点约0.5-1道题
        calculated = max(5, min(30, int(count * 0.7)))
        
        return calculated
    
    def _determine_question_types(self, knowledge_points: List[Dict]) -> List[str]:
        """根据知识点类型确定题目类型分布"""
        types = [kp.get("type", "vocabulary") for kp in knowledge_points]
        
        question_types = []
        
        # 词汇类知识点：选择、填空、判断
        vocab_count = types.count("vocabulary")
        if vocab_count > 0:
            question_types.extend(["choice"] * min(4, vocab_count))
            question_types.extend(["fill"] * min(3, vocab_count))
            question_types.extend(["true_false"] * min(2, vocab_count))
        
        # 语法类知识点：选择、填空
        grammar_count = types.count("grammar")
        if grammar_count > 0:
            question_types.extend(["choice"] * min(3, grammar_count))
            question_types.extend(["fill"] * min(2, grammar_count))
        
        # 句型类知识点：填空、语境练习
        sentence_count = types.count("sentence")
        if sentence_count > 0:
            question_types.extend(["fill"] * min(2, sentence_count))
            question_types.extend(["context"] * min(1, sentence_count))
        
        # 如果知识点太少，添加一些综合题目
        if len(question_types) < 5:
            question_types.extend(["choice", "fill", "true_false"])
        
        return question_types[:15]  # 限制题目类型列表长度
    
    def _calculate_time_limit(self, question_count: int) -> int:
        """计算测试时间限制（分钟）"""
        # 每道题约1-2分钟
        return max(10, min(60, question_count * 1.5))
    
    def _generate_backup_questions(self,
                                   knowledge_points: List[Dict],
                                   question_types: List[str],
                                   count: int) -> List[Dict]:
        """
        生成备用题目（当大模型调用失败时使用）
        """
        questions = []
        
        for i, kp in enumerate(knowledge_points[:count]):
            q_type = question_types[i % len(question_types)] if i < len(question_types) else "choice"
            
            question = {
                "type": q_type,
                "question": f"请选择正确的答案：{kp.get('content', '')} 的中文意思是？",
                "options": [
                    f"A. {kp.get('chinese_meaning', '未知')}",
                    "B. 选项2",
                    "C. 选项3",
                    "D. 选项4"
                ],
                "answer": "A",
                "explanation": f"{kp.get('content', '')} 的意思是 {kp.get('chinese_meaning', '未知')}",
                "knowledge_point": kp.get("content", "")
            }
            
            questions.append(question)
        
        return questions
    
    def grade_test(self, 
                   test: Dict, 
                   answers: List[Dict]) -> Dict[str, Any]:
        """
        批改测试
        
        Args:
            test: 测试信息
            answers: 用户答案列表
        
        Returns:
            批改结果
        """
        questions = test.get("questions", [])
        correct_count = 0
        wrong_answers = []
        correct_answers = []
        
        # 标准化答案比较
        def normalize_answer(answer: str) -> str:
            if answer is None:
                return ""
            return str(answer).strip().lower()
        
        for answer in answers:
            question_id = answer.get("question_id")
            user_answer = normalize_answer(answer.get("answer"))
            
            # 找到对应的题目
            for q in questions:
                if q.get("question") == question_id or q.get("id") == question_id:
                    correct_answer = normalize_answer(q.get("answer"))
                    is_correct = user_answer == correct_answer
                    
                    if is_correct:
                        correct_count += 1
                        correct_answers.append({
                            "question": q.get("question"),
                            "your_answer": answer.get("answer"),
                            "correct_answer": q.get("answer"),
                            "explanation": q.get("explanation")
                        })
                    else:
                        wrong_answers.append({
                            "question": q.get("question"),
                            "question_type": q.get("type"),
                            "user_answer": answer.get("answer"),
                            "correct_answer": q.get("answer"),
                            "explanation": q.get("explanation"),
                            "knowledge_point": q.get("knowledge_point"),
                            "question_content": q
                        })
                    break
        
        # 计算得分
        total = len(answers)
        score = (correct_count / total * 100) if total > 0 else 0
        passed = score >= 60  # 60%及格
        
        return {
            "total_questions": total,
            "correct_count": correct_count,
            "wrong_count": total - correct_count,
            "score": round(score, 2),
            "passed": passed,
            "correct_answers": correct_answers,
            "wrong_answers": wrong_answers
}
    
    def generate_wrong_test(self, 
                           wrong_answers: List[Dict],
                           knowledge_points: List[Dict],
                           difficulty: str = "medium") -> Dict[str, Any]:
        """
        根据错题生成针对性练习
        
        Args:
            wrong_answers: 错题列表
            knowledge_points: 知识点列表
            difficulty: 难度等级
        
        Returns:
            针对性练习
        """
        # 提取错题涉及的知识点
        wrong_kps = []
        for wa in wrong_answers:
            kp_content = wa.get("knowledge_point", "")
            for kp in knowledge_points:
                if kp.get("content", "") == kp_content:
                    wrong_kps.append(kp)
                    break
        
        # 生成针对性测试
        test_scope = {
            "type": "review",
            "description": "错题复习测试",
            "wrong_count": len(wrong_answers)
        }
        
        return self.generate_test(
            knowledge_points=wrong_kps,
            test_scope=test_scope,
            difficulty=difficulty,
            question_count=len(wrong_kps)
        )


# 创建全局测试生成器实例
test_generator = TestGenerator()
