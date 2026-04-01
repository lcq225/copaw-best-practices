---
name: meta-harness
description: Agent 输出质量评估与经验回溯系统 - 自动评估+经验存储+智能索引
---

# Meta-Harness

> GitHub: https://github.com/lcq225/meta-harness

> 基于斯坦福论文 Meta-Harness 理念的 Agent 质量保障系统

## 概述

为 CoPaw 提供自动质量评估和经验回溯能力：

| 功能 | 说明 | 状态 |
|------|------|------|
| 自动评估 | 每次输出后多维度评分 | ✅ |
| 经验存储 | SQLite 结构化存储 | ✅ |
| 智能索引 | 高价值经验存记忆系统 | ✅ |
| 统计查询 | 成功率/工具效果分析 | ✅ |

## 评估维度

| 维度 | 权重 |
|------|------|
| 正确性 | 30% |
| 完整性 | 20% |
| 效率 | 15% |
| 可维护性 | 15% |
| 安全性 | 10% |
| 测试覆盖 | 10% |

## 使用方式

### 1. Python API

```python
# 评估输出
from harness_evaluator import quick_evaluate

result = quick_evaluate("实现登录功能", login_code)
print(f"总分: {result.overall_score}")
print(f"反馈: {result.feedback}")
```

```python
# 记录经验
from experience_tracker import ExperienceTracker

tracker = ExperienceTracker()
tracker.record(
    task="实现登录",
    output=login_code,
    evaluation={"overall_score": 85},
    tools_used=["code"]
)
stats = tracker.get_stats()
```

### 2. 自动触发

集成到 CoPaw 后自动运行，无需手动调用。

## 文件结构

```
meta-harness/
├── SKILL.md                    # 本文档
├── README.md                    # 详细文档
├── harness_evaluator/          # 评估器
│   ├── __init__.py
│   ├── evaluate.py
│   ├── metrics/
│   │   ├── correctness.py
│   │   └── completeness.py
│   └── fusion.py
├── experience_tracker/          # 经验系统
│   ├── __init__.py
│   └── tracker.py
└── docs/
    └── README.md                # 架构文档
```

## CoPaw 集成

详见 README.md

## 版本

1.0.0 - 初始版本