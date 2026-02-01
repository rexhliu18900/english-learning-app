"""
英语学习辅助应用 - 文档解析服务

支持PDF、Word、PPT文件解析，提取知识点
"""

import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from pathlib import Path
import json

from config import settings


class BaseParser(ABC):
    """文档解析基类"""
    
    @abstractmethod
    def parse(self, file_path: str) -> Dict[str, Any]:
        """解析文档，返回结构化数据"""
        pass
    
    @abstractmethod
    def extract_knowledge_points(self, content: str) -> List[Dict]:
        """从内容中提取知识点"""
        pass


class WordParser(BaseParser):
    """Word文档解析器"""
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """解析Word文档"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            full_text = []
            
            for paragraph in doc.paragraphs:
                full_text.append(paragraph.text)
            
            content = '\n'.join(full_text)
            
            # 提取知识点
            knowledge_points = self.extract_knowledge_points(content)
            
            # 统计信息
            statistics = {
                "total_words": len(knowledge_points),
                "vocabulary_count": len([kp for kp in knowledge_points if kp["type"] == "vocabulary"]),
                "grammar_count": len([kp for kp in knowledge_points if kp["type"] == "grammar"]),
                "sentence_count": len([kp for kp in knowledge_points if kp["type"] == "sentence"]),
            }
            
            return {
                "success": True,
                "content": content,
                "knowledge_points": knowledge_points,
                "statistics": statistics
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_knowledge_points(self, content: str) -> List[Dict]:
        """从Word文档内容中提取知识点"""
        knowledge_points = []
        lines = content.split('\n')
        
        current_unit = None
        current_page = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测单元标题
            unit_match = re.match(r'^##?\s*(Unit\s*\d+)', line, re.IGNORECASE)
            if unit_match:
                current_unit = unit_match.group(1)
                continue
            
            # 检测页码
            page_match = re.match(r'^###?\s*p\.(\d+)', line)
            if page_match:
                current_page = page_match.group(1)
                continue
            
            # 检测词汇条目（**单词** /音标/ *词性* 中文）
            vocab_match = re.match(r'\*\*([^*]+)\*\*\s*/?([^\n*]*)\*?\.?\s*(.+)', line)
            if vocab_match:
                word = vocab_match.group(1).strip()
                phonetic = ""
                meaning = vocab_match.group(3).strip()
                
                # 提取音标
                phonetic_match = re.search(r'/([^/]+)/', line)
                if phonetic_match:
                    phonetic = phonetic_match.group(1).strip()
                
                # 提取词性
                pos_match = re.search(r'\*n\.\*|\*v\.\*|\*adj\.\*|\*adv\.\*|\*prep\.|\*conj\.|\*pron\.|\*num\.|\*det\.', line)
                pos = ""
                if pos_match:
                    pos_text = pos_match.group(0)
                    if "n." in pos_text:
                        pos = "noun"
                    elif "v." in pos_text:
                        pos = "verb"
                    elif "adj." in pos_text:
                        pos = "adjective"
                    elif "adv." in pos_text:
                        pos = "adverb"
                    elif "prep." in pos_text:
                        pos = "preposition"
                    elif "conj." in pos_text:
                        pos = "conjunction"
                    elif "pron." in pos_text:
                        pos = "pronoun"
                    elif "num." in pos_text:
                        pos = "numeral"
                    elif "det." in pos_text:
                        pos = "determiner"
                
                # 提取词组
                collocations = []
                collocation_patterns = [
                    r'([a-z]+\s+[a-z]+(?:\s+[a-z]+)*)\s*\([^)]+\)',  # 如 "be scared of (doing sth.)"
                    r'([a-z]+\s+[a-z]+(?:\s+[a-z]+)*)\s+\+',  # 如 "be afraid of +"
                ]
                
                for pattern in collocation_patterns:
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    collocations.extend(matches)
                
                knowledge_points.append({
                    "type": "vocabulary",
                    "content": word,
                    "phonetic": phonetic,
                    "part_of_speech": pos,
                    "chinese_meaning": meaning,
                    "unit": current_unit,
                    "page": current_page,
                    "collocations": list(set(collocations)) if collocations else []
                })
                continue
            
            # 检测普通词组/表达
            if line.startswith('- ') or line.startswith('* '):
                phrase = line[2:].strip()
                if current_unit:
                    knowledge_points.append({
                        "type": "phrase",
                        "content": phrase,
"unit": current_unit,
                        "page": current_page,
                        "chinese_meaning": ""
                    })
        
        return knowledge_points


class MarkdownParser(BaseParser):
    """Markdown文档解析器（用于词汇表）"""
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """解析Markdown文档"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            knowledge_points = self.extract_knowledge_points(content)
            
            # 统计信息
            statistics = {
                "total_words": len(knowledge_points),
                "vocabulary_count": len([kp for kp in knowledge_points if kp["type"] == "vocabulary"]),
                "phrase_count": len([kp for kp in knowledge_points if kp["type"] == "phrase"]),
                "grammar_count": 0,
                "sentence_count": 0,
            }
            
            return {
                "success": True,
                "content": content,
                "knowledge_points": knowledge_points,
                "statistics": statistics
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_knowledge_points(self, content: str) -> List[Dict]:
        """从Markdown内容中提取知识点"""
        knowledge_points = []
        lines = content.split('\n')
        
        current_unit = None
        current_page = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测单元标题
            unit_match = re.match(r'^##?\s*(Unit\s*\d+)', line, re.IGNORECASE)
            if unit_match:
                current_unit = unit_match.group(1)
                continue
            
            # 检测页码
            page_match = re.match(r'^###?\s*p\.(\d+)', line)
            if page_match:
                current_page = page_match.group(1)
                continue
            
            # 检测分隔线
            if '—' in line and len(line) > 20:
                continue
            
            # 检测词汇条目
            vocab_match = re.match(r'\*\*([^*]+)\*\*\s*(?:/\s*([^\n*]*)\s*)?(?:\*\.\s*)?(.+)?', line)
            if vocab_match:
                word = vocab_match.group(1).strip()
                phonetic = (vocab_match.group(2) or "").strip()
                meaning = (vocab_match.group(3) or "").strip()
                
                # 提取词性
                pos = ""
                pos_match = re.search(r'\*n\.\*|\*v\.\*|\*adj\.\*|\*adv\.\*|\*prep\.|\*conj\.|\*pron\.|\*num\.', line)
                if pos_match:
                    pos_text = pos_match.group(0)
                    if "n." in pos_text:
                        pos = "noun"
                    elif "v." in pos_text:
                        pos = "verb"
                    elif "adj." in pos_text:
                        pos = "adjective"
                    elif "adv." in pos_text:
                        pos = "adverb"
                
                # 提取词组
                collocations = []
                collocation_patterns = [
                    r'([a-z]+\s+[a-z]+(?:\s+[a-z]+)*)\s*\([^)]+\)',
                ]
                
                for pattern in collocation_patterns:
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    collocations.extend(matches)
                
                knowledge_points.append({
                    "type": "vocabulary",
                    "content": word,
                    "phonetic": phonetic,
                    "part_of_speech": pos,
                    "chinese_meaning": meaning,
                    "unit": current_unit,
                    "page": current_page,
                    "collocations": list(set(collocations)) if collocations else []
                })
                continue
            
            # 检测普通词组
            if (line.startswith('- ') or line.startswith('* ')) and len(line) > 3:
                phrase = line[2:].strip()
                if current_unit and not phrase.startswith('http'):
                    knowledge_points.append({
                        "type": "phrase",
                        "content": phrase,
                        "unit": current_unit,
                        "page": current_page,
                        "chinese_meaning": ""
                    })
        
        return knowledge_points


class PDFParser(BaseParser):
    """PDF文档解析器"""
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """解析PDF文档"""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(file_path)
            full_text = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                full_text.append(f"--- Page {page_num + 1} ---\n{text}")
            
            content = '\n'.join(full_text)
            
            # 提取知识点（简化版）
            knowledge_points = self.extract_knowledge_points(content)
            
            statistics = {
                "total_words": len(knowledge_points),
                "vocabulary_count": len([kp for kp in knowledge_points if kp["type"] == "vocabulary"]),
                "phrase_count": len([kp for kp in knowledge_points if kp["type"] == "phrase"]),
                "grammar_count": 0,
                "sentence_count": 0,
            }
            
            return {
                "success": True,
                "content": content,
                "knowledge_points": knowledge_points,
                "statistics": statistics
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_knowledge_points(self, content: str) -> List[Dict]:
        """从PDF内容中提取知识点（简化版）"""
        knowledge_points = []
        
        # 检测词汇（简化正则）
        vocab_patterns = [
            r'\*\*([A-Za-z]+)\*\*\s*/([^\n]+)/\s*\*([^\.]+)\*\.?\s*(.+)',  # **word** /phonetic/ *pos* meaning
        ]
        
        for pattern in vocab_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                word = match.group(1)
                phonetic = match.group(2)
                pos = match.group(3)
                meaning = match.group(4)
                
                knowledge_points.append({
                    "type": "vocabulary",
                    "content": word,
                    "phonetic": phonetic,
                    "part_of_speech": pos,
                    "chinese_meaning": meaning,
                    "unit": None,
                    "page": None,
                    "collocations": []
                })
        
        return knowledge_points


class DocumentParser:
    """文档解析工厂"""
    
    @staticmethod
    def get_parser(file_path: str) -> BaseParser:
        """根据文件类型获取解析器"""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.docx' or ext == '.doc':
            return WordParser()
        elif ext == '.md':
            return MarkdownParser()
        elif ext == '.pdf':
            return PDFParser()
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
    
    @staticmethod
    def parse(file_path: str) -> Dict[str, Any]:
        """解析文档"""
        parser = DocumentParser.get_parser(file_path)
        return parser.parse(file_path)
    
    @staticmethod
    def parse_and_save(file_path: str, output_path: str) -> Dict[str, Any]:
        """解析文档并保存结果"""
        result = DocumentParser.parse(file_path)
        
        if result["success"]:
            # 保存知识点到JSON文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result
