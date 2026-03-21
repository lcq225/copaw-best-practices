# 技能共享机制

> **版本：** 1.0
> **用途：** 全局/局部技能划分、继承规则、避免重复建设

---

## 一、问题背景

在多 Agent 环境下，如果每个 Agent 都维护一套完整技能：

| 问题 | 影响 |
|------|------|
| 重复存储 | 磁盘空间浪费 |
| 版本不一致 | 同名技能行为不同 |
| 维护困难 | 更新需要改多处 |
| 经验不共享 | 每个 Agent 都要重新学习 |

---

## 二、解决方案

### 目录结构

```
.copaw\
├── active_skills/           ← 全局技能（所有 Agent 共享）
│   ├── memorycoreclaw/      # 记忆系统
│   ├── docx/                # Word 处理
│   ├── pdf/                 # PDF 处理
│   ├── xlsx/                # Excel 处理
│   └── ...
│
└── workspaces/
    ├── default/             ← Agent A
    │   └── active_skills/   ← Agent A 特有技能
    │       └── cron/
    │
    └── agent-b/             ← Agent B
        └── active_skills/   ← Agent B 特有技能
            └── email/
```

### 继承规则

```python
def get_skill(skill_name, agent_id):
    """
    技能查找顺序
    """
    # 1. 先找局部技能
    局部路径 = f".copaw/workspaces/{agent_id}/active_skills/{skill_name}"
    if exists(局部路径):
        return load_skill(局部路径)
    
    # 2. 再找全局技能
    全局路径 = f".copaw/active_skills/{skill_name}"
    if exists(全局路径):
        return load_skill(全局路径)
    
    # 3. 都没有
    return None
```

**口诀：局部优先，全局兜底**

---

## 三、分类原则

### 放全局技能

| 特征 | 示例 |
|------|------|
| 所有 Agent 都需要 | `memorycoreclaw`（记忆系统） |
| 功能通用、无差异 | `docx`, `pdf`, `xlsx`（文档处理） |
| 需要统一维护 | `windows-commands`（系统命令） |

### 放局部技能

| 特征 | 示例 |
|------|------|
| 仅特定 Agent 需要 | `cron`（定时任务） |
| 有个性化配置 | `email`（邮箱配置不同） |
| 需要隔离使用 | 特定业务技能 |

---

## 四、实践案例

### 案例 1：文档处理技能

**问题：** 所有 Agent 都需要处理 Word/PDF/Excel

**解决：** 放全局
```
.copaw\active_skills\
├── docx/
├── pdf/
└── xlsx/
```

### 案例 2：定时任务技能

**问题：** 只有 Agent A 需要定时任务

**解决：** 放局部
```
.copaw\workspaces\default\active_skills\
└── cron/
```

### 案例 3：记忆系统技能

**问题：** 所有 Agent 都需要记忆，但要共享数据

**解决：** 放全局 + 共享数据库
```
.copaw\active_skills\
└── memorycoreclaw/

.copaw\.agent-memory\
└── memory.db  ← 共享数据库
```

---

## 五、维护规则

### 新增技能流程

```
1. 判断是否所有 Agent 都需要
   └─ 是 → 放全局
   └─ 否 → 放局部

2. 检查是否已有同名技能
   └─ 有 → 评估是否合并或重命名

3. 编写 SKILL.md 文档
4. 测试验证
5. 记录到记忆系统
```

### 删除技能流程

```
1. 确认无其他 Agent 依赖
2. 备份技能代码
3. 删除技能目录
4. 更新文档
5. 通知相关 Agent
```

### 版本更新流程

```
1. 全局技能更新
   └─ 需要测试对所有 Agent 的影响

2. 局部技能更新
   └─ 仅影响当前 Agent
```

---

## 六、常见问题

### Q1: 局部和全局有同名技能怎么办？

**A:** 局部优先。Agent 会使用自己的局部版本，忽略全局版本。

**建议：** 除非有特殊需求，否则删除局部版本，统一使用全局版本。

### Q2: 如何判断技能应该放全局还是局部？

**A:** 问自己两个问题：
1. 其他 Agent 需要这个技能吗？
2. 这个技能的配置对所有 Agent 都一样吗？

如果两个问题都是"是"，放全局；否则放局部。

### Q3: 全局技能更新后，所有 Agent 都受影响吗？

**A:** 是的。所以更新全局技能要谨慎，建议：
1. 先在测试环境验证
2. 灰度发布（部分 Agent 先用）
3. 监控反馈

---

## 七、最佳实践

1. **能放全局就放全局** — 减少重复
2. **定期清理重复技能** — 每月检查一次
3. **统一命名规范** — 方便查找和管理
4. **文档齐全** — 每个技能都有 SKILL.md
5. **版本控制** — 重要技能保留历史版本

---

## 八、相关文档

- [Agent 团队治理](agent-management.md)
- [MemoryCoreClaw 技能](../skills/memorycoreclaw/)