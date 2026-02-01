"""
英语学习辅助应用 - 大模型服务

集成阿里云百炼（通义千问）API
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from openai import OpenAI
from config import settings


class LLMService:
    """大模型服务类"""
    
    def __init__(self):
        """初始化大模型客户端"""
        self.client = OpenAI(
            api_key=settings.dashscope.api_key,
            base_url=settings.dashscope.base_url
        )
        self.model = "qwen-max"  # 使用通义千问Max模型
    
    def chat(self, messages: List[Dict[str, str]], 
             system_prompt: Optional[str] = None,
             temperature: float = 0.7,
             max_tokens: int = 2000) -> str:
        """
        发送对话请求
        
        Args:
            messages: 对话消息列表 [{"role": "user", "content": "..."}]
            system_prompt: 系统提示词
            temperature: 温度参数（0-2），越低越确定
            max_tokens: 最大输出token数
        
        Returns:
            模型生成的回复文本
        """
        try:
            # 构建消息列表
            chat_messages = []
            
            if system_prompt:
                chat_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            chat_messages.extend(messages)
            
            # 调用API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=chat_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"调用大模型失败: {str(e)}"
    
    def generate_questions(self, 
                          knowledge_points: List[Dict],
                          question_types: List[str] = ["choice", "fill"],
                          difficulty: str = "medium",
                          count: int = 10) -> List[Dict]:
        """
        生成测试题目
        
        Args:
            knowledge_points: 知识点列表
            question_types: 题目类型列表
            difficulty: 难度等级
            count: 题目数量
        
        Returns:
            生成的题目列表
        """
        # 构建提示词
        system_prompt = """你是专业的英语教师，擅长根据知识点生成高质量的英语测试题目。
你生成的题目应该：
1. 准确反映知识点内容
2. 选项设置合理，具有区分度
3. 题目表述清晰易懂
4. 答案准确无误

请严格按照JSON格式返回题目列表。"""
        
        # 构建知识点描述
        kp_summary = []
        for kp in knowledge_points[:20]:  # 限制知识点数量
            kp_summary.append({
                "type": kp.get("type", "vocabulary"),
                "content": kp.get("content", ""),
                "meaning": kp.get("chinese_meaning", ""),
                "example": kp.get("examples", [])[0] if kp.get("examples") else ""
            })
        
        user_prompt = f"""根据以下知识点生成{count}道测试题目：

知识点：
{json.dumps(kp_summary, ensure_ascii=False, indent=2)}

要求：
- 题目类型：{', '.join(question_types)}
- 难度等级：{difficulty}
- 题目总数：{count}

请按以下JSON格式返回（不要添加任何其他内容）：
{{
    "questions": [
        {{
            "type": "choice/fill/true_false/context",
            "question": "题目内容",
            "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],  // 选择题需要
            "answer": "正确答案",
            "explanation": "解析说明",
            "knowledge_point": "关联的知识点内容"
        }}
    ]
}}"""
        
        try:
            response = self.chat(
                messages=[{"role": "user", "content": user_prompt}],
                system_prompt=system_prompt,
                temperature=0.5,  # 较低的确定性
                max_tokens=3000
            )
            
            # 解析JSON响应
            # 尝试提取JSON内容
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                return result.get("questions", [])
            else:
                # 如果没有找到JSON，返回空列表
                return []
                
        except json.JSONDecodeError:
            return []
        except Exception as e:
            return []
    
    def answer_question(self, 
                       question: str,
                       knowledge_context: str) -> Dict[str, str]:
        """
        回答用户问题（基于知识库）
        
        Args:
            question: 用户问题
            knowledge_context: 相关知识点上下文
        
        Returns:
            回答结果
        """
        system_prompt = """你是专业的英语学习助手，根据提供的教材知识点回答用户的问题。
回答要求：
1. 基于提供的知识点内容回答
2. 回答准确、清晰
3. 适当提供相关知识点推荐
4. 如果知识点中没有相关信息，诚实说明"""
        
        user_prompt = f"""知识点上下文：
{knowledge_context}

用户问题：{question}

请回答用户的问题。"""
        
        response = self.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=1000
        )
        
        return {
            "answer": response,
            "question": question
        }
    
    def explain_knowledge_point(self, knowledge_point: Dict) -> str:
        """
        解释知识点
        
        Args:
            knowledge_point: 知识点字典
        
        Returns:
            知识点解释
        """
        system_prompt = """你是专业的英语教师，擅长解释英语词汇、语法和句型的用法。
解释要求：
1. 清晰说明词汇/语法/句型的含义和用法
2. 提供典型例句
3. 说明常见的搭配和用法
4. 适当提供易混淆点的区分"""
        
        user_prompt = f"""请详细解释以下英语知识点：

类型：{knowledge_point.get('type', 'vocabulary')}
内容：{knowledge_point.get('content', '')}
音标：{knowledge_point.get('phonetic', '')}
词性：{knowledge_point.get('part_of_speech', '')}
中文释义：{knowledge_point.get('chinese_meaning', '')}
词组搭配：{', '.join(knowledge_point.get('collocations', []))}
例句：{json.dumps(knowledge_point.get('examples', []), ensure_ascii=False)}"""
        
        response = self.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=1500
        )
        
        return response
    
    def analyze_errors(self, 
                      wrong_answers: List[Dict],
                      knowledge_points: List[Dict]) -> Dict[str, Any]:
        """
        错题分析
        
        Args:
            wrong_answers: 错误答题记录
            knowledge_points: 相关知识点
        
        Returns:
            分析结果
        """
        system_prompt = """你是专业的英语教师，擅长分析学生的错误并提供针对性的学习建议。
分析要求：
1. 识别错误的类型（概念不清、记忆错误、理解偏差等）
2. 分析错误原因
3. 提供针对性的正确解释
4. 给出学习建议"""
        
        # 构建错题信息
        error_summary = []
        for wa in wrong_answers:
            error_summary.append({
                "question": wa.get("question_content", {}).get("question", ""),
                "user_answer": wa.get("user_answer", ""),
                "correct_answer": wa.get("correct_answer", ""),
                "knowledge_point": wa.get("knowledge_point", "")
            })
        
        user_prompt = f"""请分析以下错题：

错题详情：
{json.dumps(error_summary, ensure_ascii=False, indent=2)}

请提供：
1. 错误原因分析
2. 正确知识点回顾
3. 学习建议

请按以下JSON格式返回：
{{
    "error_types": ["概念不清", "记忆错误"],
    "analysis": "综合分析...",
    "suggestions": ["建议1", "建议2"],
    "review_points": ["复习要点1", "复习要点2"]
}}"""
        
        response = self.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=system_prompt,
            temperature=0.4,
            max_tokens=2000
        )
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"analysis": response}
                
        except (json.JSONDecodeError, ValueError):
            return {"analysis": response}


# 创建全局大模型服务实例
llm_service = LLMService()
