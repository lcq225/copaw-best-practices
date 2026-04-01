# -*- coding: utf-8 -*-
"""
融合脚本：harness-evaluator + experience-tracker

实现两个技能的无缝融合：
- 评估结果自动记录到经验系统
- 经验系统可触发评估
"""
import sys
import os
from pathlib import Path

# 添加路径
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "harness-evaluator"))
sys.path.insert(0, str(BASE_DIR / "experience-tracker"))

from evaluate import HarnessEvaluator, EvaluationResult
from tracker import ExperienceTracker, ExperienceRecord


class HarnessExperienceFusion:
    """
    评估器与经验系统融合
    
    实现双向融合：
    1. 评估结果 → 自动记录到经验系统
    2. 经验系统 → 基于历史给出评估建议
    """
    
    def __init__(self):
        self.evaluator = HarnessEvaluator()
        self.tracker = ExperienceTracker()
    
    def evaluate_and_record(self, task: str, output: str, 
                            context: dict = None) -> EvaluationResult:
        """
        评估并记录
        
        1. 评估 Agent 输出
        2. 记录到经验系统
        
        Args:
            task: 任务描述
            output: Agent 输出
            context: 上下文
            
        Returns:
            EvaluationResult: 评估结果
        """
        context = context or {}
        
        # 1. 评估
        result = self.evaluator.evaluate(task, output, context)
        
        # 2. 记录到经验系统
        self.tracker.record(
            task=task,
            output=output,
            evaluation=result.to_dict(),
            tools_used=context.get("tools_used", []),
            context=context,
            tags=context.get("tags", [])
        )
        
        return result
    
    def get_evaluation_advice(self, task: str) -> dict:
        """
        基于历史经验获取评估建议
        
        Args:
            task: 当前任务
            
        Returns:
            建议字典
        """
        # 搜索相似任务
        similar = self.tracker.search_similar(task, limit=3)
        
        advice = {
            "has_history": len(similar) > 0,
            "similar_count": len(similar),
            "recommendations": []
        }
        
        if similar:
            # 从历史中提取评估相关的建议
            for record in similar:
                if record.evaluation:
                    score = record.evaluation.get("overall_score", 0)
                    if score >= 80:
                        advice["recommendations"].append({
                            "task": record.task,
                            "score": score,
                            "suggestion": "历史成功案例，可参考"
                        })
                    elif score < 60:
                        advice["recommendations"].append({
                            "task": record.task,
                            "score": score,
                            "suggestion": "历史失败案例，需避免"
                        })
        
        # 如果没有历史，返回通用建议
        if not advice["recommendations"]:
            advice["recommendations"].append({
                "task": task,
                "suggestion": "无历史记录，建议按标准流程评估"
            })
        
        return advice
    
    def batch_evaluate_and_record(self, tasks: list) -> list:
        """
        批量评估并记录
        
        Args:
            tasks: [{"task": "...", "output": "..."}, ...]
            
        Returns:
            评估结果列表
        """
        results = []
        for item in tasks:
            result = self.evaluate_and_record(
                item["task"],
                item["output"],
                item.get("context", {})
            )
            results.append(result)
        
        return results


# ============== 便捷函数 ==============

def quick_evaluate_record(task: str, output: str, **kwargs) -> EvaluationResult:
    """快速评估并记录"""
    fusion = HarnessExperienceFusion()
    return fusion.evaluate_and_record(task, output, kwargs)


def get_advice(task: str) -> dict:
    """快速获取评估建议"""
    fusion = HarnessExperienceFusion()
    return fusion.get_evaluation_advice(task)


__all__ = [
    "HarnessExperienceFusion",
    "quick_evaluate_record",
    "get_advice"
]


if __name__ == "__main__":
    # 测试融合
    fusion = HarnessExperienceFusion()
    
    # 测试评估并记录
    result = fusion.evaluate_and_record(
        task="测试融合：实现加法函数",
        output="def add(a, b): return a + b",
        context={"tools_used": ["code"]}
    )
    
    print(f"评估总分: {result.overall_score}")
    print(f"评估分数: {result.scores}")
    
    # 测试获取建议
    advice = fusion.get_evaluation_advice("实现减法函数")
    print(f"建议: {advice}")
    
    print("\n融合测试通过!")