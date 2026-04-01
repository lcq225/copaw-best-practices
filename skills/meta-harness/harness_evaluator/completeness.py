# -*- coding: utf-8 -*-
"""
完整性评分模块
"""
import re
from typing import Dict, List, Set


class CompletenessMetric:
    """完整性评分"""
    
    @classmethod
    def evaluate(cls, task: str, output: str, context: Dict = None) -> float:
        """
        评估完整性
        
        Args:
            task: 任务描述
            output: Agent 输出
            context: 上下文
            
        Returns:
            0-100 的分数
        """
        context = context or {}
        score = 70  # 基础分数
        
        # 1. 检查输出长度
        output_len = len(output.strip())
        if output_len < 50:
            score -= 30
        elif output_len < 100:
            score -= 15
        elif output_len < 200:
            score -= 5
        
        # 2. 提取关键词并检查覆盖率
        keywords = cls._extract_keywords(task)
        if keywords:
            found = cls._count_keywords(output, keywords)
            coverage = found / len(keywords)
            score = score * 0.5 + coverage * 50
        
        # 3. 检查任务类型特定的完整性
        task_type = context.get("task_type", cls._guess_task_type(task))
        score = cls._check_type_specific(task, output, task_type, score)
        
        return max(0, min(100, score))
    
    @classmethod
    def _extract_keywords(cls, task: str) -> Set[str]:
        """提取任务关键词"""
        # 中文
        chinese = set(re.findall(r'[\u4e00-\u9fff]{2,}', task))
        
        # 英文
        english = set(re.findall(r'[a-zA-Z]{3,}', task))
        
        # 过滤停用词
        stop_words = {
            'the', 'a', 'an', 'to', 'of', 'in', 'for', 'with', 'on', 'at',
            '实现', '功能', '一个', '如何', '怎么', '请', '帮我',
            '的', '了', '是', '在', '和', '与', '或', '需要'
        }
        
        chinese = chinese - stop_words
        english = {w.lower() for w in english} - stop_words
        
        return chinese | english
    
    @classmethod
    def _count_keywords(cls, output: str, keywords: Set[str]) -> int:
        """统计关键词出现次数"""
        found = 0
        output_lower = output.lower()
        
        for kw in keywords:
            if kw.lower() in output_lower:
                found += 1
        
        return found
    
    @classmethod
    def _guess_task_type(cls, task: str) -> str:
        """猜测任务类型"""
        task_lower = task.lower()
        
        if any(w in task_lower for w in ['api', '接口', '函数', '方法']):
            return 'function'
        elif any(w in task_lower for w in ['class', '类', '对象']):
            return 'class'
        elif any(w in task_lower for w in ['test', '测试', '用例']):
            return 'test'
        elif any(w in task_lower for w in ['script', '脚本', '工具']):
            return 'script'
        elif any(w in task_lower for w in ['config', '配置']):
            return 'config'
        else:
            return 'general'
    
    @classmethod
    def _check_type_specific(cls, task: str, output: str, 
                            task_type: str, score: float) -> float:
        """检查类型特定的完整性"""
        if task_type == 'function':
            # 检查函数定义
            if 'def ' not in output and 'function ' not in output.lower():
                score -= 20
        
        elif task_type == 'class':
            # 检查类定义
            if 'class ' not in output:
                score -= 20
        
        elif task_type == 'test':
            # 检查测试框架
            if not any(w in output.lower() for w in ['test', 'assert', 'expect', 'should']):
                score -= 20
        
        elif task_type == 'config':
            # 检查配置格式
            if not any(c in output for c in ['{', '}', '[', ']', ':', '=']):
                score -= 15
        
        return score
    
    @classmethod
    def get_missing_items(cls, task: str, output: str) -> List[str]:
        """获取缺失项"""
        keywords = cls._extract_keywords(task)
        missing = []
        
        for kw in keywords:
            if kw.lower() not in output.lower():
                missing.append(kw)
        
        return missing[:5]  # 最多返回5个