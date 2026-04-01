# -*- coding: utf-8 -*-
"""
正确性评分模块
"""
import re
from typing import Dict, List


class CorrectnessMetric:
    """正确性评分"""
    
    # 严重错误模式
    CRITICAL_ERRORS = [
        "SyntaxError",
        "NameError", 
        "TypeError",
        "ImportError",
        "AttributeError",
        "KeyError",
        "ValueError",
        "IndexError",
    ]
    
    # 警告模式
    WARNINGS = [
        "TODO",
        "FIXME",
        "XXX",
        "HACK",
    ]
    
    @classmethod
    def evaluate(cls, output: str, context: Dict = None) -> float:
        """
        评估正确性
        
        Args:
            output: 待评估的输出
            context: 上下文信息
            
        Returns:
            0-100 的分数
        """
        context = context or {}
        score = 100
        
        # 检查严重错误
        for error in cls.CRITICAL_ERRORS:
            if error in output:
                score -= 25
        
        # 检查警告标记
        for warning in cls.WARNINGS:
            if warning in output:
                score -= 10
        
        # 检查空输出
        if not output or len(output.strip()) < 10:
            score -= 50
        
        # 检查异常模式
        score -= cls._check_exception_patterns(output)
        
        return max(0, min(100, score))
    
    @classmethod
    def _check_exception_patterns(cls, output: str) -> int:
        """检查异常模式"""
        penalty = 0
        
        # 检查 except: without handling
        if re.search(r'except\s*:', output):
            penalty += 5
        
        # 检查 raise NotImplementedError without implementation
        if 'raise NotImplementedError' in output and 'NotImplementedError' not in output:
            penalty += 15
        
        # 检查 return outside function
        if re.search(r'^\s*return\s+[^None]', output, re.MULTILINE):
            # 简单检查，可能误判
            pass
        
        return penalty
    
    @classmethod
    def get_issues(cls, output: str) -> List[str]:
        """获取问题列表"""
        issues = []
        
        for error in cls.CRITICAL_ERRORS:
            if error in output:
                issues.append(f"可能存在 {error}")
        
        for warning in cls.WARNINGS:
            if warning in output:
                issues.append(f"存在未完成标记: {warning}")
        
        return issues