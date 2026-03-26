# CoPaw 记忆系统最佳实践

> 本文档总结了 CoPaw 记忆系统的使用技巧和优化经验，包括 MemoryCoreClaw 技能的增强实现。

## 一、记忆系统架构

### 1.1 分层记忆设计

```
┌─────────────────────────────────────────────────────────────┐
│                     分层记忆架构                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   MEMORY.md（工作记忆/热数据）                               │
│   - 核心身份、偏好、路径                                     │
│   - 最近工作上下文、进行中任务                               │
│   - 常用联系人、核心教训                                     │
│   - 自动加载，快速热启动                                     │
│                                                             │
│   memory.db（长期记忆/冷数据）                               │
│   - 事实记忆、经验教训                                       │
│   - 实体关系、情境记忆                                       │
│   - 向量语义搜索                                             │
│                                                             │
│   memory/*.md（每日笔记）                                    │
│   - 今日工作、会议纪要                                       │
│   - 定期沉淀到 memory.db                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 数据库表结构

| 表名 | 用途 | 关键字段 |
|------|------|---------|
| `facts` | 事实记忆 | id, content, category, importance, status, source, source_confidence |
| `experiences` | 经验教训 | id, action, context, outcome, insight, source |
| `todos` | 待办事项 | id, task, priority, status, done_at |
| `decision_changelog` | 决策变更日志 | old_decision_id, new_decision_id, topic, change_type |
| `relations` | 实体关系 | from_entity, relation_type, to_entity |
| `entities` | 实体定义 | name, type, importance |

---

## 二、压缩功能优化

### 2.1 问题：ReActAgent 注入干扰

**问题描述：**
CoPaw 默认使用 ReMe 的 `Compactor`，内部使用 `ReActAgent`。这会导致：
- 注入 tools 列表
- 注入 skill prompt
- 模型输出包含无关内容

**解决方案：创建 DirectCompactor**

```python
# memorycoreclaw/core/direct_compactor.py

class DirectCompactor:
    """直接调用模型的压缩器，绕过 ReActAgent"""
    
    async def compact(
        self,
        messages: List[Msg],
        previous_summary: str = "",
    ) -> Dict[str, Any]:
        # 构建消息（字典格式，不是 Msg 对象）
        msgs = [
            {"role": "system", "content": COMPACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        
        # 直接调用模型
        response = await self.model(msgs)
        
        # 解析记忆提取 JSON
        memory_extraction = self._parse_memory_extraction(content)
        
        return {
            "history_compact": content,
            "memory_extraction": memory_extraction,
            "is_valid": is_valid,
        }
```

### 2.2 压缩提示词设计

```
你是一个专业的上下文压缩助手。你的任务是将对话历史压缩成简洁的摘要，同时提取重要的记忆信息。

## 输出格式要求

### 一、对话摘要
[用简洁的语言总结对话的核心内容]

### 四、记忆提取
```json
{
  "decisions": [{"decision": "做了什么决定", "reason": "决定原因"}],
  "lessons": [{"lesson": "学到了什么", "context": "在什么情境下"}],
  "todos": [{"task": "待办事项", "priority": "high/medium/low"}],
  "facts": [{"fact": "需要记住的事实", "category": "technical/preference/project"}]
}
```
```

### 2.3 流式 vs 非流式

**结论：对用户使用无影响**

| 方式 | 内部实现 | 用户体验 |
|------|----------|----------|
| 流式 | 边生成边处理 chunk | 无感知 |
| 非流式 | 一次性返回 | 无感知 |

真正影响的是 ReActAgent 注入问题，而非流式/非流式。

---

## 三、决策生命周期管理

### 3.1 核心设计

```python
# 决策状态
status: active | superseded

# 决策主题（自动推断）
topic: compression_model | embedding_model | architecture | other

# 来源可信度
source: user | compaction | system | document
source_confidence: 0.85 ~ 1.0
```

### 3.2 决策更新流程

```
用户添加新决策
     │
     ▼
推断决策主题 (topic)
     │
     ▼
查找同主题的 active 决策
     │
     ├─── 有旧决策 ───▶ 标记为 superseded，记录变更日志
     │
     ▼
写入新决策 (status=active)
```

### 3.3 使用示例

```python
from memorycoreclaw.core.enhanced_memory import get_enhanced_memory

mem = get_enhanced_memory()

# 记录用户决策（可信度 1.0）
mem.remember_decision(
    decision="使用 GLM-5 作为压缩模型",
    reason="海科网关支持，中文能力强",
    source="user",
)

# 记录压缩提取决策（可信度 0.85）
mem.remember_decision(
    decision="使用 DeepSeek 作为压缩模型",
    reason="成本低",
    source="compaction",
)

# 查看当前有效决策
decisions = mem.get_active_decisions(topic="compression_model")
```

---

## 四、来源可信度分层

### 4.1 可信度配置

| 来源 | 可信度 | 说明 |
|------|--------|------|
| `user` | 1.0 | 用户明确输入 |
| `user_explicit` | 1.0 | 用户明确说"记住这个" |
| `user_statement` | 0.95 | 用户说出的内容 |
| `system` | 0.95 | 系统配置 |
| `compaction` | 0.85 | LLM 压缩提取（智能推断） |
| `document` | 0.8 | 从文档读取 |

### 4.2 冲突处理原则

```
1. 同主题决策：新决策取代旧决策
2. 不同可信度：检索时可按可信度排序
3. 用户确认：提升压缩提取决策的可信度
```

---

## 五、向量搜索集成

### 5.1 Ollama 本地部署

```bash
# 拉取向量模型
ollama pull bge-large:335m

# 启动服务
ollama serve
# 默认地址：http://127.0.0.1:11434
```

### 5.2 智能去重

```python
def _is_duplicate_enhanced(self, content: str, threshold: float = 0.90) -> bool:
    """使用向量相似度检查是否重复"""
    
    # 获取查询向量
    query_embedding = self._get_embedding(content)
    
    # 计算与现有记录的相似度
    for existing_content in existing_records:
        existing_embedding = self._get_embedding(existing_content)
        similarity = self._cosine_similarity(query_embedding, existing_embedding)
        
        if similarity >= threshold:
            return True  # 重复
    
    return False
```

### 5.3 相似度阈值建议

| 场景 | 阈值 | 说明 |
|------|------|------|
| 决策去重 | 0.92 | 更严格，避免不同决策被误判 |
| 教训去重 | 0.90 | 中等 |
| 事实去重 | 0.90 | 中等 |

---

## 六、定期清理策略

### 6.1 清理配置

| 数据类型 | 保留时间 | 清理条件 |
|----------|----------|----------|
| superseded 决策 | 40 天 | 被取代后超过 40 天 |
| 已完成待办 | 180 天 | 完成后超过半年 |

### 6.2 清理脚本

```python
# memorycoreclaw/scripts/cleanup_memory.py

def cleanup_memory(db_path: str, dry_run: bool = False):
    """清理旧记录"""
    
    # 清理 superseded 决策
    cursor.execute('''
        DELETE FROM facts 
        WHERE category = 'decision' 
        AND status = 'superseded' 
        AND datetime(updated_at) < datetime('now', '-40 days')
    ''')
    
    # 清理已完成待办
    cursor.execute('''
        DELETE FROM todos 
        WHERE status = 'done' 
        AND datetime(done_at) < datetime('now', '-180 days')
    ''')
```

### 6.3 定时任务

```bash
# 创建每周清理任务（周日凌晨3点）
copaw cron create \
  --type agent \
  --name "每周记忆清理" \
  --cron "0 3 * * 0" \
  --channel console \
  --target-user default \
  --target-session default \
  --text "执行记忆系统清理，删除过期决策和已完成待办"
```

---

## 七、检索效率优化

### 7.1 数据库 vs 文件

| 指标 | 文件存储 | 数据库存储 |
|------|----------|------------|
| 检索时间 | 秒级 | 毫秒级 |
| 随机访问 | 需扫描全部 | 索引查询 |
| 并发支持 | 差 | 好 |
| 事务支持 | 无 | 有 |

### 7.2 索引优化

```sql
-- 常用查询索引
CREATE INDEX idx_facts_category ON facts(category);
CREATE INDEX idx_facts_status ON facts(status);
CREATE INDEX idx_facts_topic ON facts(topic);
CREATE INDEX idx_todos_status ON todos(status);
```

---

## 八、最佳实践总结

### 8.1 记忆写入

```python
# 用户明确决策 → source='user'
mem.remember_decision(
    decision="使用 PostgreSQL 作为主数据库",
    reason="支持复杂查询和高并发",
    source="user",
)

# 压缩提取决策 → source='compaction'
mem.remember_decision(
    decision="使用向量搜索提高检索效率",
    reason="语义匹配比关键词更准确",
    source="compaction",
)

# 重要教训 → importance=0.9
mem.learn(
    action="未备份直接修改配置",
    context="修改 config.json 前未备份",
    outcome="negative",
    insight="修改前必须备份",
    importance=0.9
)
```

### 8.2 记忆检索

```python
# 按关键词搜索
results = mem.recall("压缩模型", limit=5)

# 按主题搜索
decisions = mem.get_active_decisions(topic="compression_model")

# 按分类搜索
preferences = mem.recall_by_category("preference")

# 按可信度筛选
high_confidence = mem.recall_by_confidence(min_confidence=0.9)
```

### 8.3 定期维护

```python
# 每周执行一次清理
mem.cleanup_old_records()

# 每月检查数据库状态
stats = mem.get_stats()
print(f"事实: {stats['total_facts']}")
print(f"教训: {stats['total_experiences']}")
```

---

## 九、常见问题

### Q1: 压缩输出包含无关内容？

**原因：** ReActAgent 注入了 tools 和 skill prompt

**解决：** 使用 DirectCompactor 绕过 ReActAgent

### Q2: 决策重复出现？

**原因：** 没有生命周期管理

**解决：** 使用 `remember_decision()` 自动管理

### Q3: 检索效率慢？

**原因：** 使用文件存储

**解决：** 迁移到数据库，添加索引

### Q4: 压缩模型调整影响使用？

**回答：** 不影响。问题在于 ReActAgent 注入，而非流式/非流式

---

## 十、参考资源

- [MemoryCoreClaw 技能文档](../skills/memorycoreclaw/)
- [CoPaw 官方文档](https://github.com/agentscope-ai/CoPaw)
- [Ollama 官方文档](https://ollama.ai/)