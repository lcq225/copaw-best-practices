"""
更新记忆数据库 - 添加今天的里程碑事件
"""

import sqlite3
import sys
import os
from datetime import datetime

# 数据库路径
def get_db_path():
    if 'MEMORY_DB_PATH' in os.environ:
        return os.environ['MEMORY_DB_PATH']
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.path.join(os.getcwd(), '.copaw', '.agent-memory', 'memory.db')

DB_PATH = get_db_path()

def update_memory():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("更新记忆数据库")
    print("=" * 60)
    
    # 1. 添加 PR 合并的里程碑记忆
    print("\n📝 添加里程碑记忆...")
    
    new_facts = [
        ("CoPaw PR #1601 已合并，修复 Windows GBK 编码 Bug", 0.9, "milestone", "positive"),
        ("ReMe PR #1 已合并，修复 Windows GBK 编码 Bug", 0.9, "milestone", "positive"),
        ("2026-03-20：首次成功向开源项目贡献代码并被合并", 0.95, "milestone", "positive"),
        ("MemoryCoreClaw 项目已发布到 GitHub", 0.85, "project", "positive"),
        ("MemoryCoreClaw 仓库地址：https://github.com/lcq225/MemoryCoreClaw", 0.8, "project", "neutral"),
        ("开源贡献完整记录在 _老K输出/笔记/2026-03-17_开源贡献里程碑完整记录.md", 0.75, "reference", "neutral"),
    ]
    
    for content, importance, category, emotion in new_facts:
        # 检查是否已存在
        cursor.execute("SELECT id FROM facts WHERE content LIKE ?", (f"%{content[:30]}%",))
        if cursor.fetchone():
            print(f"   已存在: {content[:40]}...")
            continue
        
        cursor.execute('''
            INSERT INTO facts (content, importance, category, emotion, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (content, importance, category, emotion, datetime.now().isoformat()))
        
        fact_id = cursor.lastrowid
        
        # 添加记忆强度
        cursor.execute('''
            INSERT INTO memory_strength (memory_type, memory_id, base_strength, current_strength, access_count, last_accessed)
            VALUES ('fact', ?, ?, ?, 1, ?)
        ''', (fact_id, importance, importance, datetime.now().isoformat()))
        
        print(f"   ✅ 添加: {content[:50]}...")
    
    # 2. 添加新的教训
    print("\n📚 添加经验教训...")
    
    new_lessons = [
        ("文档整理要定期进行", "知识管理", "positive", "7篇旧文章合并为2篇，知识库更精简", 0.8),
        ("教程需要及时更新", "技术文档", "positive", "外部资源变化快，定期更新保证准确性", 0.75),
    ]
    
    for action, context, outcome, insight, importance in new_lessons:
        cursor.execute('''
            INSERT INTO experiences (action, context, outcome, insight, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (action, context, outcome, insight, importance, datetime.now().isoformat()))
        
        exp_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO memory_strength (memory_type, memory_id, base_strength, current_strength, access_count, last_accessed)
            VALUES ('experience', ?, ?, ?, 1, ?)
        ''', (exp_id, importance, importance, datetime.now().isoformat()))
        
        print(f"   ✅ 添加: {action}")
    
    # 3. 添加新关系
    print("\n🔗 添加实体关系...")
    
    new_relations = [
        ("MemoryCoreClaw", "developed_by", "Mr Lee", 0.9, "个人项目"),
        ("MemoryCoreClaw", "github_url", "https://github.com/lcq225/MemoryCoreClaw", 0.8, "项目链接"),
        ("CoPaw PR #1601", "merged_into", "CoPaw", 0.9, "开源贡献"),
        ("ReMe PR #1", "merged_into", "ReMe", 0.9, "开源贡献"),
    ]
    
    for from_entity, relation_type, to_entity, weight, evidence in new_relations:
        cursor.execute('''
            SELECT id FROM relations WHERE from_entity = ? AND relation_type = ? AND to_entity = ?
        ''', (from_entity, relation_type, to_entity))
        
        if cursor.fetchone():
            print(f"   已存在: {from_entity} --[{relation_type}]--> {to_entity}")
            continue
        
        cursor.execute('''
            INSERT INTO relations (from_entity, relation_type, to_entity, weight, evidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (from_entity, relation_type, to_entity, weight, evidence, datetime.now().isoformat()))
        
        print(f"   ✅ 添加: {from_entity} --[{relation_type}]--> {to_entity}")
    
    conn.commit()
    
    # 4. 统计
    print("\n" + "=" * 60)
    print("📊 更新后统计")
    print("=" * 60)
    
    cursor.execute("SELECT COUNT(*) FROM facts")
    facts_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM experiences")
    exp_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM relations")
    rel_count = cursor.fetchone()[0]
    
    print(f"""
📝 事实记忆：{facts_count} 条
📚 经验教训：{exp_count} 条
🔗 实体关系：{rel_count} 条
""")
    
    conn.close()
    
    print("✅ 记忆更新完成！")
    print("=" * 60)

if __name__ == "__main__":
    update_memory()