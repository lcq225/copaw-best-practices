# Meta-Harness for CoPaw

> Agent 输出质量评估与经验回溯系统

## 安装

```bash
# 方式1：复制到 CoPaw 技能目录
cp -r meta-harness/ $COPAW/active_skills/

# 方式2：pip 安装
pip install meta-harness/
```

## CoPaw 集成

### 1. 复制集成模块

```bash
# 创建集成文件（需要手动创建）
# src/copaw/agents/harness_integration.py
```

详细集成步骤见 README.md

## 使用

```python
# 评估输出
from meta_harness.harness_evaluator import quick_evaluate

result = quick_evaluate("任务", output_code)
print(f"得分: {result.overall_score}")

# 记录经验
from meta_harness.experience_tracker import ExperienceTracker

tracker = ExperienceTracker()
tracker.record(task="任务", output=output)
```

## 版本

1.0.0