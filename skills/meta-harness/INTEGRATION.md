# Meta-Harness CoPaw 集成指南

本文档说明如何将 Meta-Harness 集成到 CoPaw 中。

## 概述

Meta-Harness 在 CoPaw 中实现自动：
1. 任务执行后评估输出质量
2. 记录到 SQLite 数据库
3. 高价值经验索引到记忆系统

## 集成步骤

### 步骤1：复制技能文件

```bash
# 复制 meta-harness 到 CoPaw 技能目录
cp -r meta-harness/ $COPAW/active_skills/
```

### 步骤2：创建集成模块

创建文件 `src/copaw/agents/harness_integration.py`：

```python
# -*- coding: utf-8 -*-
"""
Harness 自动集成模块
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# 全局配置
AUTO_EVALUATE_ENABLED = True
AUTO_RECORD_ENABLED = True
AUTO_INDEX_ENABLED = True
LOW_SCORE_THRESHOLD = 60
HIGH_SCORE_THRESHOLD = 80


class HarnessIntegration:
    def __init__(self, agent_name: str = "unknown"):
        self.agent_name = agent_name
        self._initialized = False

    def _ensure_initialized(self):
        if not self._initialized:
            import sys
            from pathlib import Path
            
            # 添加技能路径
            base_dir = Path(__file__).parent.parent.parent.parent / "workspaces" / "default" / "active_skills"
            sys.path.insert(0, str(base_dir / "harness-evaluator"))
            sys.path.insert(0, str(base_dir / "experience-tracker"))
            self._initialized = True

    async def on_task_complete(self, task: str, output: Any, 
                               tools_used: list = None, context: Dict = None) -> Dict:
        """任务完成回调"""
        self._ensure_initialized()
        
        result = {"score": 0, "record_id": None, "suggestions": []}
        
        if not AUTO_EVALUATE_ENABLED and not AUTO_RECORD_ENABLED:
            return result

        output_str = str(output) if output else ""
        if not output_str or len(output_str) < 10:
            return result

        try:
            # 1. 评估
            if AUTO_EVALUATE_ENABLED:
                score = await self._evaluate(task, output_str)
                result["score"] = score

            # 2. 记录
            if AUTO_RECORD_ENABLED:
                record_id = await self._record(task, output_str, result["score"], tools_used, context)
                result["record_id"] = record_id

                # 3. 索引到 memory
                if AUTO_INDEX_ENABLED and result["score"] > 0:
                    await self._index_to_memory(task, result["score"], tools_used, record_id)

        except Exception as e:
            logger.warning(f"[Harness] Processing failed: {e}")

        return result

    async def _evaluate(self, task: str, output: str) -> float:
        try:
            from evaluate import quick_evaluate
            result = quick_evaluate(task, output)
            return result.overall_score
        except Exception as e:
            logger.warning(f"[Harness] Evaluate failed: {e}")
            return 0

    async def _record(self, task: str, output: str, score: float, 
                      tools_used: list, context: Dict) -> str:
        try:
            from tracker import ExperienceTracker
            tracker = ExperienceTracker()
            record = tracker.record(
                task=task, output=output,
                evaluation={"overall_score": score} if score > 0 else None,
                tools_used=tools_used or [], context=context or {}
            )
            return str(record.id)
        except Exception as e:
            logger.warning(f"[Harness] Record failed: {e}")
            return ""

    async def _index_to_memory(self, task: str, score: float, 
                               tools_used: list, record_id: str):
        should_index = False
        importance = 0.6
        category = "experience"

        if score >= HIGH_SCORE_THRESHOLD:
            should_index = True
            importance = 0.8
            category = "success_experience"
        elif score < LOW_SCORE_THRESHOLD:
            should_index = True
            importance = 0.9
            category = "failure_lesson"

        if not should_index:
            return

        try:
            import sys
            from pathlib import Path
            base_dir = Path(__file__).parent.parent.parent.parent / "workspaces" / "default"
            sys.path.insert(0, str(base_dir / "skills"))
            from memorycoreclaw import SafeMemory
            
            mem = SafeMemory(db_path=str(base_dir / ".copaw" / ".agent-memory" / "memory.db"))
            
            tools_str = ", ".join(tools_used) if tools_used else "无"
            score_status = "成功" if score >= HIGH_SCORE_THRESHOLD else "失败"
            
            memory_content = f"任务: {task[:100]}... | 评估分数: {score} ({score_status}) | 使用工具: {tools_str} | 记录ID: {record_id}"
            
            mem.remember(memory_content, importance=importance, category=category, source="system")
            
        except Exception as e:
            logger.warning(f"[Harness] Memory index failed: {e}")
```

### 步骤3：修改 tool_guard_mixin.py

在 `src/copaw/agents/tool_guard_mixin.py` 中：

1. 在文件顶部添加导入：
```python
from copaw.agents.harness_integration import HarnessIntegration
```

2. 在 `_init_tool_guard()` 方法中添加：
```python
if HarnessIntegration:
    self.harness = HarnessIntegration(agent_name=self.__class__.__name__)
```

3. 在 `_acting()` 方法末尾添加：
```python
if hasattr(self, 'harness'):
    await self.harness.on_task_complete(
        task=task_description,
        output=str(result),
        tools_used=[tool_name],
        context={"agent": self.__class__.__name__}
    )
```

### 步骤4：验证

```bash
python -c "from copaw.agents.tool_guard_mixin import ToolGuardMixin; print('OK')"
```

## 配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| AUTO_EVALUATE_ENABLED | True | 自动评估 |
| AUTO_RECORD_ENABLED | True | 自动记录 |
| AUTO_INDEX_ENABLED | True | 自动索引 |
| LOW_SCORE_THRESHOLD | 60 | 低分阈值 |
| HIGH_SCORE_THRESHOLD | 80 | 高分阈值 |

## 数据存储

- **experiences.db**: SQLite 数据库，位于 CoPaw 工作区
- **memory.db**: 记忆系统数据库，自动索引高/低分经验