"""
将 memory.db 同步到 MEMORY.md

这样 CoPaw 就能读取我们的记忆数据
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path


def sync_memory_db_to_md(db_path: str, md_path: str):
    """将数据库记忆同步到 MEMORY.md"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取统计
    cursor.execute("SELECT COUNT(*) FROM facts")
    facts_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM experiences")
    exp_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM relations")
    rel_count = cursor.fetchone()[0]

    # 获取所有事实记忆（按重要性排序）
    cursor.execute("""
        SELECT content, importance, category, created_at
        FROM facts
        ORDER BY importance DESC, created_at DESC
    """)
    facts = cursor.fetchall()

    # 获取所有经验教训
    cursor.execute("""
        SELECT action, context, outcome, insight, importance, created_at
        FROM experiences
        ORDER BY importance DESC, created_at DESC
    """)
    experiences = cursor.fetchall()

    # 获取所有实体关系
    cursor.execute("""
        SELECT from_entity, relation_type, to_entity, weight
        FROM relations
        ORDER BY weight DESC
    """)
    relations = cursor.fetchall()

    conn.close()

    # 生成 Markdown 内容
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    md_content = f"""# 长期记忆

> **✅ MemoryCoreClaw 已部署**
>
> 类人脑记忆系统已激活，数据存储在加密数据库中。
>
> **最后同步：** {now}

---

## 📊 记忆统计

```
📝 事实记忆：{facts_count} 条
📚 经验教训：{exp_count} 条
🔗 实体关系：{rel_count} 条
```

---

## 📝 事实记忆（按重要性排序）

| # | 类别 | 内容 | 重要性 |
|---|------|------|--------|
"""

    # 添加事实
    for i, (content, importance, category, created_at) in enumerate(facts, 1):
        # 截断过长的内容
        short_content = content[:80] + "..." if len(content) > 80 else content
        md_content += f"| {i} | {category or '-'} | {short_content} | {importance:.1f} |\n"

    md_content += """
---

## 📚 经验教训

| # | 情境 | 教训 | 重要性 |
|---|------|------|--------|
"""

    # 添加经验
    for i, (action, context, outcome, insight, importance, created_at) in enumerate(experiences, 1):
        short_context = (context[:40] + "...") if context and len(context) > 40 else (context or "-")
        short_insight = (insight[:50] + "...") if insight and len(insight) > 50 else (insight or "-")
        md_content += f"| {i} | {short_context} | {short_insight} | {importance:.1f} |\n"

    md_content += """
---

## 🔗 实体关系

| 实体1 | 关系 | 实体2 | 强度 |
|-------|------|-------|------|
"""

    # 添加关系
    for from_entity, relation_type, to_entity, weight in relations:
        try:
            w = float(weight) if weight else 0.0
        except:
            w = 0.0
        md_content += f"| {from_entity} | {relation_type} | {to_entity} | {w:.1f} |\n"

    md_content += """
---

## 💾 数据存储

- **数据库路径：** `D:\\CoPaw\\.copaw\\.agent-memory\\memory.db`
- **数据是真实存储在数据库中，此文件为同步备份**
- **使用 `check_memory.py` 查看完整数据**
"""

    # 写入文件
    Path(md_path).write_text(md_content, encoding="utf-8")

    print(f"✅ 已同步 {facts_count} 条事实, {exp_count} 条经验, {rel_count} 条关系到 MEMORY.md")
    return facts_count + exp_count + rel_count


if __name__ == "__main__":
    db_path = r"D:\CoPaw\.copaw\.agent-memory\memory.db"
    md_path = r"D:\CoPaw\.copaw\workspaces\default\MEMORY.md"

    sync_memory_db_to_md(db_path, md_path)