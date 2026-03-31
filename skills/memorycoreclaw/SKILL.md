---
name: memorycoreclaw
description: 类人脑长期记忆系统 - 支持分层记忆、遗忘曲线、情境记忆、关系网络
---

# MemoryCoreClaw Skill

> 类人脑长期记忆系统

## 功能概述

为 CoPaw 提供类人脑的长期记忆能力：

| 功能 | 说明 |
|------|------|
| **分层记忆** | 核心层/重要层/普通层/次要层 |
| **遗忘曲线** | Ebbinghaus 模型，记忆强度随时间衰减 |
| **情境记忆** | 按人物、地点、活动等情境触发记忆 |
| **工作记忆** | 短期暂存，容量限制 (7±2) |
| **关系学习** | 实体间的关系网络 |

## 目录结构

```
active_skills/memorycoreclaw/
├── core/           # 核心引擎
├── cognitive/      # 认知模块（遗忘曲线、情境记忆）
├── retrieval/      # 检索模块
├── storage/        # 存储模块
├── utils/          # 工具模块
├── scripts/        # 管理脚本
│   ├── check_memory.py         # 检查数据库状态
│   ├── update_memory.py        # 更新记忆数据
│   ├── init_memory.py          # 初始化数据库
│   ├── optimize_database.py    # 优化数据库
│   ├── record_session_lessons.py  # 记录会话教训
│   ├── auto_check.py           # 自动检查
│   ├── sync_to_memory_md.py    # 同步到 MEMORY.md
│   └── create_entities_for_relations.py  # 为关系创建实体
└── SKILL.md        # 本文档
```

## 数据库位置

```
你的CoPaw路径\.copaw\.agent-memory\memory.db
```

**配置方式：**
```python
# 在使用时指定数据库路径
from memorycoreclaw import Memory
mem = Memory(db_path=r"你的路径\.copaw\.agent-memory\memory.db")
```

## 使用方法

### 初始化

```python
import sys
sys.path.insert(0, 'active_skills')
from memorycoreclaw import Memory

# 请替换为你的实际数据库路径
mem = Memory(db_path=r"你的路径\.copaw\.agent-memory\memory.db")
```

### 记住事实

```python
# 基础用法
mem.remember("Mr Lee 在某大型化工集团工作", importance=0.9)

# 带分类和情感
mem.remember(
    "Mr Lee 喜欢 BLUF 沟通风格",
    importance=0.8,
    category="preference",
    emotion="positive"
)
```

### 召回记忆

```python
# 关键词搜索
results = mem.recall("工作", limit=5)

# 按分类搜索
results = mem.recall_by_category("preference")

# 按重要性筛选
results = mem.recall_by_importance(min_importance=0.7)
```

### 学习经验教训

```python
mem.learn(
    action="未备份直接修改配置",
    context="系统升级",
    outcome="negative",
    insight="修改前必须备份",
    importance=0.9
)
```

### 建立关系

```python
mem.relate("Mr Lee", "works_at", "某化工集团")
mem.relate("某化工集团", "located_in", "山东")

# 查询关系
relations = mem.get_relations("Mr Lee")
```

### 工作记忆

```python
# 暂存信息
mem.hold("current_task", "写文档", priority=0.9)

# 取出信息
task = mem.retrieve("current_task")

# 清空工作记忆
mem.clear_working_memory()
```

## 管理脚本

```bash
# 检查数据库状态
python active_skills/memorycoreclaw/scripts/check_memory.py

# 更新记忆数据（从 MEMORY.md 导入）
python active_skills/memorycoreclaw/scripts/update_memory.py

# 初始化新数据库
python active_skills/memorycoreclaw/scripts/init_memory.py

# 优化数据库（清理、修复、补充）
python active_skills/memorycoreclaw/scripts/optimize_database.py
```

## 重要性分级

| 分数 | 级别 | 说明 |
|------|------|------|
| ≥0.9 | 核心记忆 | 永久保留，注入上下文 |
| 0.7-0.9 | 重要记忆 | 长期保留 |
| 0.5-0.7 | 普通记忆 | 正常保留 |
| <0.5 | 次要记忆 | 可能衰减 |

## 更新时机

| 场景 | 操作 | 重要性 |
|------|------|--------|
| 用户说"记住这个" | remember() | 0.7+ |
| 用户偏好/习惯 | remember() | 0.8+ |
| 项目信息 | remember() | 0.7+ |
| 重要决策 | remember() | 0.8+ |
| 犯错/教训 | learn() | 0.8+ |
| 实体关系 | relate() | - |

## 工具函数

### 查看记忆统计

```python
stats = mem.get_stats()
print(stats)
```

### 导出记忆

```python
# JSON 格式
data = mem.export()

# Markdown 格式
mem.export_markdown("memory_export.md")
```

### 清理低强度记忆

```python
# 清理强度低于 0.1 的记忆
mem.cleanup(low_strength=0.1)
```

## 可视化功能

```bash
# 生成知识图谱、统计报告、记忆浏览器
python active_skills/memorycoreclaw/utils/visualization.py
```

**输出位置：** `_老K输出/记忆可视化/`

## 相关文件

| 文件 | 用途 |
|------|------|
| `MEMORY.md` | 人类可读的记忆摘要（备份） |
| `memory/YYYY-MM-DD.md` | 每日笔记（原始记录） |
| `.agent-memory/memory.db` | 数据库（主存储） |

---

**创建时间：** 2026-03-20
**最后更新：** 2026-03-21