# -*- coding: utf-8 -*-
"""
自动触发钩子 - 让 harness-evaluator 和 experience-tracker 自动运行

使用方式：
1. 在 CoPaw 源码中集成此钩子
2. 或在任务执行后调用 auto_evaluate() / auto_record()
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, List, Optional
from functools import wraps

logger = logging.getLogger(__name__)

# 全局回调注册表
_post_task_callbacks: List[Callable] = []


def register_post_task_callback(callback: Callable):
    """
    注册任务完成后的回调函数
    
    使用示例：
    ```python
    def my_callback(task_output, context):
        # 评估输出
        result = quick_evaluate(task_output["task"], task_output["output"])
        # 记录经验
        tracker.record(task=task_output["task"], output=task_output["output"])
    
    register_post_task_callback(my_callback)
    ```
    """
    _post_task_callbacks.append(callback)
    logger.info(f"[AutoHook] Registered callback: {callback.__name__}")


async def trigger_callbacks(task_output: Dict, context: Dict) -> None:
    """
    触发所有注册的回调
    
    Args:
        task_output: 任务输出 {"task": "...", "output": "..."}
        context: 执行上下文 {"agent": "...", "tools_used": [...], ...}
    """
    for callback in _post_task_callbacks:
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(task_output, context)
            else:
                callback(task_output, context)
        except Exception as e:
            logger.warning(f"[AutoHook] Callback {callback.__name__} failed: {e}")


# ============== 自动评估和记录 ==============

def setup_auto_hooks():
    """
    设置自动钩子 - 导入并注册回调
    
    需要在 CoPaw 源码的 tool_guard_mixin.py 中调用
    """
    try:
        import sys
        from pathlib import Path
        
        # 添加路径
        base_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(base_dir / "harness-evaluator"))
        sys.path.insert(0, str(base_dir / "experience-tracker"))
        
        # 导入模块
        from evaluate import quick_evaluate
        from tracker import ExperienceTracker
        
        # 创建回调函数
        async def auto_evaluate_and_record(task_output: Dict, context: Dict):
            """自动评估并记录"""
            task = task_output.get("task", "")
            output = task_output.get("output", "")
            
            if not task or not output:
                return
            
            try:
                # 1. 评估
                result = quick_evaluate(task, output)
                
                # 2. 记录到经验系统
                tracker = ExperienceTracker()
                tracker.record(
                    task=task,
                    output=output,
                    evaluation=result.to_dict(),
                    tools_used=context.get("tools_used", []),
                    context={
                        "agent": context.get("agent", "unknown"),
                        "evaluation_score": result.overall_score
                    }
                )
                
                logger.info(f"[AutoHook] Evaluated and recorded: {task[:50]}... (score: {result.overall_score})")
                
                # 3. 如果分数低，触发 debugging 建议
                if result.overall_score < 60:
                    logger.warning(f"[AutoHook] Low score detected: {result.overall_score} - consider debugging")
                    
            except Exception as e:
                logger.warning(f"[AutoHook] Auto evaluate failed: {e}")
        
        # 注册回调
        register_post_task_callback(auto_evaluate_and_record)
        logger.info("[AutoHook] Auto hooks configured successfully")
        
    except Exception as e:
        logger.warning(f"[AutoHook] Setup failed: {e}")


# ============== 便捷函数 ==============

def auto_evaluate(task: str, output: str, context: Dict = None) -> Dict:
    """
    快速自动评估
    
    使用示例：
    ```python
    # 在任务完成后调用
    result = auto_evaluate("实现登录", generated_code)
    ```
    """
    import sys
    from pathlib import Path
    
    base_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(base_dir / "harness-evaluator"))
    
    from evaluate import quick_evaluate
    
    result = quick_evaluate(task, output, **(context or {}))
    return result.to_dict()


def auto_record(task: str, output: str, evaluation: Dict = None, **kwargs) -> str:
    """
    快速自动记录
    
    使用示例：
    ```python
    # 在任务完成后调用
    record_id = auto_record("实现登录", code, evaluation=eval_result)
    ```
    """
    import sys
    from pathlib import Path
    
    base_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(base_dir / "experience-tracker"))
    
    from tracker import ExperienceTracker
    
    tracker = ExperienceTracker()
    record = tracker.record(
        task=task,
        output=output,
        evaluation=evaluation,
        **kwargs
    )
    return record.id


# ============== CoPaw 集成说明 ==============

"""
要在 CoPaw 中集成自动触发，需要修改 src/copaw/agents/tool_guard_mixin.py：

1. 在文件顶部导入：
   from copaw.agents.auto_hooks import trigger_callbacks, setup_auto_hooks

2. 在 _acting 方法末尾（约第310行）添加：
   # 触发自动评估和记录
   await trigger_callbacks(
       task_output={"task": task_description, "output": str(result)},
       context={"agent": self.__class__.__name__, "tools_used": [tool_name]}
   )

3. 在 Agent 初始化时调用：
   setup_auto_hooks()

或者更简单的方式 - 创建一个独立的集成文件：
src/copaw/agents/harness_integration.py
"""


if __name__ == "__main__":
    # 测试
    print("Auto Hooks 配置测试")
    
    # 设置钩子
    setup_auto_hooks()
    
    # 手动触发
    import asyncio
    
    async def test_trigger():
        await trigger_callbacks(
            task_output={"task": "测试任务", "output": "def add(a,b): return a+b"},
            context={"agent": "test", "tools_used": ["code"]}
        )
    
    asyncio.run(test_trigger())
    print("测试完成")