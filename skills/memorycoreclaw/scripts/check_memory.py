"""
检查记忆数据库状态 - 增强版
功能：统计、健康检查、重复检测、路径验证

设计原则：
- 孤立关系：不自动删除，作为"待完善"提示
- 重复教训：不自动删除，提示用户确认
- 只读检查，不做破坏性操作
"""

import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path

# 数据库路径：优先使用环境变量，其次使用命令行参数，最后使用默认值
def get_db_path():
    if 'MEMORY_DB_PATH' in os.environ:
        return os.environ['MEMORY_DB_PATH']
    if len(sys.argv) > 1:
        return sys.argv[1]
    # 默认路径（相对于当前工作目录）
    return os.path.join(os.getcwd(), '.copaw', '.agent-memory', 'memory.db')

DB_PATH = get_db_path()

def check_memory():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 60)
    print("📊 MemoryCoreClaw 数据库状态检查")
    print("=" * 60)
    print(f"\n数据库路径: {DB_PATH}")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ============================================================
    # 1. 基础统计
    # ============================================================
    cursor.execute("SELECT COUNT(*) FROM facts")
    facts_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM experiences")
    exp_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM relations")
    rel_count = cursor.fetchone()[0]

    print(f"""
┌─────────────────────────────────────────────────────────┐
│  记忆统计                                                │
├─────────────────────────────────────────────────────────┤
│  📝 事实记忆    {facts_count:>3} 条                                 │
│  📚 经验教训    {exp_count:>3} 条                                 │
│  🔗 实体关系    {rel_count:>3} 条                                 │
└─────────────────────────────────────────────────────────┘
""")

    # ============================================================
    # 2. 健康检查
    # ============================================================
    print("🏥 健康检查:")
    health_issues = []
    suggestions = []

    # 2.1 检查重复教训
    duplicates = cursor.execute('''
        SELECT action, COUNT(*) as cnt
        FROM experiences
        GROUP BY action
        HAVING cnt > 1
    ''').fetchall()

    if duplicates:
        for dup in duplicates:
            health_issues.append(f"⚠️ 重复教训: '{dup[0]}' 出现 {dup[1]} 次")
            suggestions.append(f"  建议手动合并: SELECT * FROM experiences WHERE action = '{dup[0]}'")
    else:
        print("   ✅ 无重复教训")

    # 2.2 检查 migrated 分类
    migrated_count = cursor.execute('SELECT COUNT(*) FROM facts WHERE category = "migrated"').fetchone()[0]
    if migrated_count > 0:
        health_issues.append(f"⚠️ migrated 分类未清理: {migrated_count} 条")
        suggestions.append("  建议运行: python update_memory.py 重新分类")
    else:
        print("   ✅ migrated 分类已清理")

    # 2.3 检查空内容
    empty_facts = cursor.execute('SELECT COUNT(*) FROM facts WHERE content IS NULL OR content = ""').fetchone()[0]
    if empty_facts > 0:
        health_issues.append(f"⚠️ 空内容事实: {empty_facts} 条")
    else:
        print("   ✅ 无空内容记录")

    # 2.4 检查孤立关系（只提示，不删除）
    orphan_relations = cursor.execute('''
        SELECT id, from_entity, relation_type, to_entity
        FROM relations
        WHERE NOT EXISTS (SELECT 1 FROM entities WHERE entities.name = relations.from_entity)
           OR NOT EXISTS (SELECT 1 FROM entities WHERE entities.name = relations.to_entity)
    ''').fetchall()

    if orphan_relations:
        health_issues.append(f"💡 待完善关系: {len(orphan_relations)} 条（实体未在 entities 表中定义）")
        print(f"\n   💡 待完善关系 ({len(orphan_relations)}条):")
        print("      (这些关系是有效的，只是相关实体未显式定义)")
        for r in orphan_relations[:5]:  # 只显示前5条
            print(f"      • {r[1]} --[{r[2]}]--> {r[3]}")
        if len(orphan_relations) > 5:
            print(f"      ... 还有 {len(orphan_relations) - 5} 条")
        suggestions.append("  可选操作: python create_entities_for_relations.py 自动创建缺失实体")
    else:
        print("   ✅ 所有关系都有对应的实体定义")

    # 2.5 检查 memory_strength 表完整性
    try:
        strength_count = cursor.execute('SELECT COUNT(*) FROM memory_strength').fetchone()[0]
        print(f"   ✅ 记忆强度记录: {strength_count} 条")
    except:
        health_issues.append("⚠️ memory_strength 表可能损坏")

    # 输出健康问题
    if health_issues:
        print("\n   ⚠️ 发现问题:")
        for issue in health_issues:
            print(f"      {issue}")

    # ============================================================
    # 3. 分类统计
    # ============================================================
    print("\n📊 事实分类分布:")
    categories = cursor.execute('''
        SELECT category, COUNT(*) as cnt
        FROM facts
        GROUP BY category
        ORDER BY cnt DESC
    ''').fetchall()

    for cat, cnt in categories:
        bar = "█" * min(cnt // 5, 10)
        print(f"   {cat:12} {cnt:>3}条 {bar}")

    # ============================================================
    # 4. 路径有效性验证（抽样）
    # ============================================================
    print("\n📁 路径验证（抽样）:")
    import re
    path_facts = cursor.execute('''
        SELECT content FROM facts
        WHERE category = 'path' OR content LIKE '%D:\\\\%' OR content LIKE '%C:\\\\%'
        LIMIT 5
    ''').fetchall()

    for (content,) in path_facts:
        paths = re.findall(r'[A-Z]:\\[\\\\\w\-\.]+', content)
        for p in paths:
            if os.path.exists(p):
                print(f"   ✅ {p}")
            else:
                print(f"   ⚠️ {p} (不存在)")

    # ============================================================
    # 5. 最近添加的事实
    # ============================================================
    print("\n📌 最近添加的事实:")
    cursor.execute("""
        SELECT content, importance, category
        FROM facts
        ORDER BY id DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        content, importance, category = row
        print(f"   📌 [{category}] {content[:50]}...")

    # ============================================================
    # 6. 高重要性教训
    # ============================================================
    print("\n📚 高重要性教训 (importance >= 0.9):")
    cursor.execute("""
        SELECT action, insight
        FROM experiences
        WHERE importance >= 0.9
        ORDER BY importance DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        action, insight = row
        print(f"   ⚠️ {action}: {insight[:45]}...")

    # ============================================================
    # 7. 健康报告总结
    # ============================================================
    print("\n" + "=" * 60)
    print("📋 健康报告总结")
    print("=" * 60)

    total_issues = len([i for i in health_issues if i.startswith("⚠️")])
    suggestions_count = len([i for i in health_issues if i.startswith("💡")])

    if total_issues == 0 and suggestions_count == 0:
        print("\n✅ 数据库状态良好，无异常\n")
    else:
        if total_issues > 0:
            print(f"\n⚠️ 发现 {total_issues} 个需要关注的问题")
        if suggestions_count > 0:
            print(f"💡 发现 {suggestions_count} 个可选优化项")

        if suggestions:
            print("\n建议操作:")
            for s in suggestions:
                print(s)

    print("\n常用命令:")
    print("  - 定期检查: python check_memory.py")
    print("  - 优化修复: python optimize_database.py")
    print("  - 更新记忆: python update_memory.py")

    conn.close()
    print("=" * 60)

    return total_issues == 0

if __name__ == "__main__":
    check_memory()