"""
英语学习辅助应用 - 数据库模型

定义数据表结构和模型
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, 
    Text, JSON, ForeignKey, Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


def generate_uuid():
    """生成UUID"""
    return str(uuid4())


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(String(20), nullable=False)  # parent, student
    name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    family_id = Column(String(36), nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # 关联关系
    textbooks = relationship("Textbook", back_populates="owner", lazy="dynamic")
    test_records = relationship("TestRecord", back_populates="user", lazy="dynamic")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "email": self.email,
            "user_type": self.user_type,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "family_id": self.family_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None
        }


class Textbook(Base):
    """教材表"""
    __tablename__ = "textbooks"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=True)
    file_type = Column(String(20), nullable=False)  # pdf, word, ppt
    file_path = Column(String(500), nullable=False)
    parse_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    statistics = Column(JSON, nullable=True)  # 知识点统计信息
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    owner = relationship("User", back_populates="textbooks")
    units = relationship("Unit", back_populates="textbook", lazy="dynamic", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "version": self.version,
            "file_type": self.file_type,
            "parse_status": self.parse_status,
            "statistics": self.statistics,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Unit(Base):
    """单元表"""
    __tablename__ = "units"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    textbook_id = Column(String(36), ForeignKey("textbooks.id"), nullable=False, index=True)
    unit_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    page_range = Column(String(50), nullable=True)
    vocabulary_count = Column(Integer, default=0)
    grammar_count = Column(Integer, default=0)
    sentence_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    textbook = relationship("Textbook", back_populates="units")
    knowledge_points = relationship("KnowledgePoint", back_populates="unit", lazy="dynamic", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "textbook_id": self.textbook_id,
            "unit_number": self.unit_number,
            "title": self.title,
            "page_range": self.page_range,
            "vocabulary_count": self.vocabulary_count,
            "grammar_count": self.grammar_count,
            "sentence_count": self.sentence_count,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class KnowledgePoint(Base):
    """知识点表"""
    __tablename__ = "knowledge_points"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    unit_id = Column(String(36), ForeignKey("units.id"), nullable=False, index=True)
    point_type = Column(String(20), nullable=False)  # vocabulary, grammar, sentence
    content = Column(Text, nullable=False)  # 英文内容
    phonetic = Column(String(100), nullable=True)  # 音标
    part_of_speech = Column(String(20), nullable=True)  # 词性
    chinese_meaning = Column(Text, nullable=True)  # 中文释义
    collocations = Column(JSON, nullable=True)  # 词组搭配
    examples = Column(JSON, nullable=True)  # 例句
    image_description = Column(Text, nullable=True)  # 图片描述
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    unit = relationship("Unit", back_populates="knowledge_points")
    answer_records = relationship("AnswerRecord", back_populates="knowledge_point", lazy="dynamic")
    
    def to_dict(self):
        return {
            "id": self.id,
            "unit_id": self.unit_id,
            "point_type": self.point_type,
            "content": self.content,
            "phonetic": self.phonetic,
            "part_of_speech": self.part_of_speech,
            "chinese_meaning": self.chinese_meaning,
            "collocations": self.collocations,
            "examples": self.examples,
            "image_description": self.image_description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class TestRecord(Base):
    """测试记录表"""
    __tablename__ = "test_records"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    textbook_id = Column(String(36), ForeignKey("textbooks.id"), nullable=False, index=True)
    test_type = Column(String(20), nullable=False)  # unit, comprehensive
    test_scope = Column(JSON, nullable=False)  # 测试范围描述
    total_questions = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    score = Column(Float, default=0.0)  # 得分百分比
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    status = Column(String(20), default="in_progress")  # in_progress, completed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="test_records")
    answer_records = relationship("AnswerRecord", back_populates="test_record", lazy="dynamic", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "textbook_id": self.textbook_id,
            "test_type": self.test_type,
            "test_scope": self.test_scope,
            "total_questions": self.total_questions,
            "correct_count": self.correct_count,
            "score": self.score,
            "difficulty": self.difficulty,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AnswerRecord(Base):
    """答题记录表"""
    __tablename__ = "answer_records"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    test_id = Column(String(36), ForeignKey("test_records.id"), nullable=False, index=True)
    knowledge_point_id = Column(String(36), ForeignKey("knowledge_points.id"), nullable=True, index=True)
    question_type = Column(String(20), nullable=False)  # choice, fill, true_false, context
    question_content = Column(JSON, nullable=False)  # 题目内容
    user_answer = Column(Text, nullable=True)
    correct_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, default=False)
    question_difficulty = Column(String(20), default="medium")
    time_spent = Column(Integer, default=0)  # 答题耗时（秒）
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    test_record = relationship("TestRecord", back_populates="answer_records")
    knowledge_point = relationship("KnowledgePoint", back_populates="answer_records")
    
    def to_dict(self):
        return {
            "id": self.id,
            "test_id": self.test_id,
            "knowledge_point_id": self.knowledge_point_id,
            "question_type": self.question_type,
            "question_content": self.question_content,
            "user_answer": self.user_answer,
            "correct_answer": self.correct_answer,
            "is_correct": self.is_correct,
            "question_difficulty": self.question_difficulty,
            "time_spent": self.time_spent,
            "answered_at": self.answered_at.isoformat() if self.answered_at else None
        }
