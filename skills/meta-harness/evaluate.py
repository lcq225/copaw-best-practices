# -*- coding: utf-8 -*-
"""
Harness 评估器核心模块
"""
import json
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# 评估结果
@dataclass
class EvaluationResult:
    """评估结果"""
    task: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 各维度分数 (0-100)
    scores: Dict[str, float] = field(default_factory=dict)
    
    # 综合分数
    overall_score: float = 0.0
    
    # 问题列表
    issues: List[str] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # 改进建议
    feedback: List[str] = field(default_factory=list)
    
    # 原始输出
    output_length: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "task": self.task,
            "timestamp": self.timestamp,
            "scores": self.scores,
            "overall_score": self.overall_score,
            "issues": self.issues,
            "critical_issues": self.critical_issues,
            "warnings": self.warnings,
            "feedback": self.feedback,
            "output_length": self.output_length
        }


class HarnessEvaluator:
    """
    Harness 评估器
    
    多维度评估 Agent 输出质量
    """
    
    # 权重配置
    WEIGHTS = {
        "correctness": 0.30,
        "completeness": 0.20,
        "efficiency": 0.15,
        "maintainability": 0.15,
        "security": 0.10,
        "test_coverage": 0.10
    }
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
    
    def evaluate(self, task: str, output: str, 
                 context: Optional[Dict] = None) -> EvaluationResult:
        """
        评估 Agent 输出
        
        Args:
            task: 任务描述
            output: Agent 输出内容
            context: 额外上下文信息
            
        Returns:
            EvaluationResult: 评估结果
        """
        context = context or {}
        
        result = EvaluationResult(task=task)
        result.output_length = len(output)
        
        # 1. 正确性评估
        result.scores["correctness"] = self._evaluate_correctness(
            task, output, context
        )
        
        # 2. 完整性评估
        result.scores["completeness"] = self._evaluate_completeness(
            task, output, context
        )
        
        # 3. 效率评估
        result.scores["efficiency"] = self._evaluate_efficiency(
            task, output, context
        )
        
        # 4. 可维护性评估
        result.scores["maintainability"] = self._evaluate_maintainability(
            task, output, context
        )
        
        # 5. 安全性评估
        result.scores["security"] = self._evaluate_security(
            task, output, context
        )
        
        # 6. 测试覆盖评估
        result.scores["test_coverage"] = self._evaluate_test_coverage(
            task, output, context
        )
        
        # 计算综合分数
        result.overall_score = sum(
            score * self.WEIGHTS[dim] 
            for dim, score in result.scores.items()
        )
        
        # 生成问题列表和反馈
        self._generate_feedback(result, context)
        
        return result
    
    def _evaluate_correctness(self, task: str, output: str, 
                              context: Dict) -> float:
        """评估正确性"""
        score = 70  # 基础分数
        
        # 检查是否有明显错误
        error_patterns = [
            r"SyntaxError",
            r"NameError",
            r"TypeError",
            r"ImportError",
            r"NotImplementedError"
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                score -= 20
        
        # 检查是否有 TODO 或占位符
        if "TODO" in output or "FIXME" in output:
            score -= 10
        
        return max(0, min(100, score))
    
    def _evaluate_completeness(self, task: str, output: str, 
                               context: Dict) -> float:
        """评估完整性"""
        score = 70
        
        # 检查输出长度
        if len(output) < 50:
            score -= 30
        elif len(output) < 100:
            score -= 15
        
        # 检查是否包含必要的关键字
        required_keywords = self._extract_keywords(task)
        found_keywords = sum(1 for kw in required_keywords if kw.lower() in output.lower())
        
        if required_keywords:
            completeness = found_keywords / len(required_keywords)
            score = score * 0.5 + completeness * 50
        
        return max(0, min(100, score))
    
    def _evaluate_efficiency(self, task: str, output: str, 
                             context: Dict) -> float:
        """评估效率"""
        score = 80
        
        # 检查是否有明显的低效实现
        # 例如：循环内的字符串拼接
        if re.search(r"for.*\+=.*str", output, re.DOTALL):
            score -= 10
        
        # 检查是否有重复代码
        lines = [l.strip() for l in output.split('\n') if l.strip()]
        unique_lines = set(lines)
        if len(lines) > 10 and len(unique_lines) / len(lines) < 0.3:
            score -= 15
        
        return max(0, min(100, score))
    
    def _evaluate_maintainability(self, task: str, output: str, 
                                  context: Dict) -> float:
        """评估可维护性"""
        score = 70
        
        # 检查函数/方法长度
        functions = re.findall(r'def (\w+)\(.*?\):', output)
        if functions:
            # 简单检查：如果有很长的函数，扣分
            long_functions = [f for f in functions if f.startswith('_') is False]
            if len(long_functions) > 10:
                score -= 10
        
        # 检查是否有适当的注释
        comment_lines = len(re.findall(r'#.*$', output, re.MULTILINE))
        code_lines = len([l for l in output.split('\n') if l.strip() and not l.strip().startswith('#')])
        
        if code_lines > 0:
            comment_ratio = comment_lines / code_lines
            if comment_ratio < 0.05:
                score -= 10
            elif comment_ratio > 0.3:
                score -= 5  # 注释太多也不太好
        
        return max(0, min(100, score))
    
    def _evaluate_security(self, task: str, output: str, 
                          context: Dict) -> float:
        """评估安全性"""
        score = 80
        security_level = context.get("security_level", "medium")
        
        # 高安全要求检查
        if security_level == "high":
            # 检查密码是否明文存储
            if re.search(r'password\s*=\s*["\'][^"\']+["\']', output, re.IGNORECASE):
                score -= 30
            
            # 检查是否有 SQL 注入风险
            if re.search(r'.execute\s*\(\s*["\'].*\%s.*["\'].*\)', output):
                score -= 20
            
            # 检查是否有硬编码密钥
            if re.search(r'api[_-]?key\s*=\s*["\'][^"\']+["\']', output, re.IGNORECASE):
                score -= 20
        
        # 基础安全检查
        if "eval(" in output or "exec(" in output:
            score -= 25
        
        return max(0, min(100, score))
    
    def _evaluate_test_coverage(self, task: str, output: str, 
                               context: Dict) -> float:
        """评估测试覆盖"""
        score = 50  # 默认分数较低
        
        # 检查是否有测试代码
        if "test" in output.lower() or "pytest" in output.lower():
            score += 20
        
        if "assert" in output.lower():
            score += 15
        
        if "unittest" in output.lower() or "mock" in output.lower():
            score += 15
        
        return max(0, min(100, score))
    
    def _extract_keywords(self, task: str) -> List[str]:
        """从任务中提取关键词"""
        # 简单提取：中文和英文单词
        chinese = re.findall(r'[\u4e00-\u9fff]+', task)
        english = re.findall(r'[a-zA-Z]+', task)
        
        # 过滤停用词
        stop_words = {"的", "了", "是", "在", "和", "与", "the", "a", "an", "to", "of", "in", "for", "with", "on"}
        
        keywords = [w for w in chinese + english if w.lower() not in stop_words and len(w) > 1]
        
        return keywords[:10]  # 最多10个
    
    def _generate_feedback(self, result: EvaluationResult, context: Dict):
        """生成反馈建议"""
        # 关键问题
        if result.scores.get("correctness", 0) < 60:
            result.critical_issues.append("代码存在明显错误，请先修复")
        
        if result.scores.get("security", 0) < 60:
            result.critical_issues.append("存在安全风险，必须修复")
        
        # 一般问题
        if result.scores.get("completeness", 0) < 60:
            result.issues.append("输出不完整，请补充完整需求")
        
        if result.scores.get("test_coverage", 0) < 40:
            result.warnings.append("缺少测试用例，建议添加测试")
        
        # 改进建议
        if result.scores.get("maintainability", 0) < 70:
            result.feedback.append("建议添加更多注释提高可维护性")
        
        if result.scores.get("efficiency", 0) < 70:
            result.feedback.append("考虑优化算法效率")
    
    def evaluate_and_save(self, task: str, output: str, 
                          output_path: str) -> EvaluationResult:
        """评估并保存结果"""
        result = self.evaluate(task, output)
        
        # 保存为 JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        
        return result
    
    def batch_evaluate(self, tasks: List[Dict]) -> List[EvaluationResult]:
        """
        批量评估
        
        Args:
            tasks: [{"task": "...", "output": "..."}, ...]
        """
        results = []
        for item in tasks:
            result = self.evaluate(item["task"], item["output"], item.get("context", {}))
            results.append(result)
        return results
    
    def compare_results(self, results: List[EvaluationResult]) -> Dict:
        """比较多个评估结果"""
        if not results:
            return {}
        
        best = max(results, key=lambda x: x.overall_score)
        
        return {
            "total": len(results),
            "best_score": best.overall_score,
            "best_task": best.task,
            "average_score": sum(r.overall_score for r in results) / len(results),
            "scores_summary": {
                r.task: r.overall_score for r in results
            }
        }


# ============== 便捷函数 ==============

def quick_evaluate(task: str, output: str, **kwargs) -> EvaluationResult:
    """快速评估"""
    evaluator = HarnessEvaluator()
    return evaluator.evaluate(task, output, kwargs)


def evaluate_and_report(task: str, output: str, report_path: str) -> str:
    """评估并生成报告"""
    evaluator = HarnessEvaluator()
    result = evaluator.evaluate(task, output)
    
    # 生成报告
    report = f"""# 评估报告

## 任务
{task}

## 综合分数
{result.overall_score:.1f}/100

## 各维度分数
| 维度 | 分数 |
|------|------|
"""
    for dim, score in result.scores.items():
        report += f"| {dim} | {score:.1f} |\n"
    
    if result.critical_issues:
        report += "\n## 关键问题\n"
        for issue in result.critical_issues:
            report += f"- ❌ {issue}\n"
    
    if result.feedback:
        report += "\n## 改进建议\n"
        for fb in result.feedback:
            report += f"- 💡 {fb}\n"
    
    # 保存报告
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report


__all__ = [
    "HarnessEvaluator",
    "EvaluationResult",
    "quick_evaluate",
    "evaluate_and_report"
]