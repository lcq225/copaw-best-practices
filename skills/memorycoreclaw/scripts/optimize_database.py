"""
MemoryCoreClaw 数据库优化脚本
方案C: 重新设计最优架构，迁移旧数据

执行任务:
1. 清理空表 (facts_v2, experiences_v2, entities_v2)
2. 补充缺失的 memory_strength 记录
3. 从 relations 提取 entities
4. 修复 engine.py 字段不匹配问题
5. 验证数据完整性
"""

import sqlite3
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# 数据库路径：优先使用环境变量，其次使用命令行参数，最后使用默认值
def get_db_path():
    if 'MEMORY_DB_PATH' in os.environ:
        return Path(os.environ['MEMORY_DB_PATH'])
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    return Path(os.path.join(os.getcwd(), '.copaw', '.agent-memory', 'memory.db'))

DB_PATH = get_db_path()

def backup_database():
    """备份数据库"""
    import shutil
    backup_path = DB_PATH.parent / f"memory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(DB_PATH, backup_path)
    print(f"✅ 已备份数据库到: {backup_path}")
    return backup_path

def get_stats(cursor):
    """获取统计信息"""
    stats = {}
    tables = ['facts', 'experiences', 'relations', 'entities', 
              'memory_strength', 'contexts', 'memory_context_bindings',
              'facts_v2', 'experiences_v2', 'entities_v2']
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]
        except:
            stats[table] = 'N/A'
    return stats

def clean_empty_tables(cursor):
    """清理空表"""
    print("\n" + "=" * 60)
    print("🗑️ 清理空表")
    print("=" * 60)
    
    # 检查并删除空表（先检查表是否存在）
    empty_tables = ['facts_v2', 'experiences_v2', 'entities_v2']
    dropped = []
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}
    
    for table in empty_tables:
        if table not in existing_tables:
            print(f"  ⏭️ 表 {table} 不存在，跳过")
            continue
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            dropped.append(table)
            print(f"  ✅ 已删除空表: {table}")
        else:
            print(f"  ⚠️ 表 {table} 有 {count} 条记录，保留")
    
    return dropped

def fix_memory_strength(cursor):
    """补充缺失的 memory_strength 记录"""
    print("\n" + "=" * 60)
    print("🔧 补充 memory_strength 记录")
    print("=" * 60)
    
    now = datetime.now().isoformat()
    
    # 获取所有 facts 的 ID
    cursor.execute("SELECT id, importance FROM facts")
    facts = cursor.fetchall()
    
    # 获取已存在的 memory_strength 记录
    cursor.execute("SELECT memory_id FROM memory_strength WHERE memory_type = 'fact'")
    existing_ids = set(row[0] for row in cursor.fetchall())
    
    added = 0
    for fact_id, importance in facts:
        if fact_id not in existing_ids:
            cursor.execute("""
                INSERT INTO memory_strength 
                (memory_type, memory_id, base_strength, current_strength, 
                 access_count, last_accessed, last_decay, retention_rate)
                VALUES (?, ?, ?, ?, 0, ?, ?, 1.0)
            """, ('fact', fact_id, importance or 0.5, importance or 0.5, now, now))
            added += 1
    
    print(f"  ✅ 为 facts 补充了 {added} 条 memory_strength 记录")
    
    # 获取所有 experiences 的 ID
    cursor.execute("SELECT id, importance FROM experiences")
    experiences = cursor.fetchall()
    
    # 获取已存在的 memory_strength 记录
    cursor.execute("SELECT memory_id FROM memory_strength WHERE memory_type = 'experience'")
    existing_ids = set(row[0] for row in cursor.fetchall())
    
    added = 0
    for exp_id, importance in experiences:
        if exp_id not in existing_ids:
            cursor.execute("""
                INSERT INTO memory_strength 
                (memory_type, memory_id, base_strength, current_strength, 
                 access_count, last_accessed, last_decay, retention_rate)
                VALUES (?, ?, ?, ?, 0, ?, ?, 1.0)
            """, ('experience', exp_id, importance or 0.5, importance or 0.5, now, now))
            added += 1
    
    print(f"  ✅ 为 experiences 补充了 {added} 条 memory_strength 记录")
    
    return added

def extract_entities_from_relations(cursor):
    """从 relations 提取 entities"""
    print("\n" + "=" * 60)
    print("📦 从 relations 提取 entities")
    print("=" * 60)
    
    # 获取所有唯一的实体
    cursor.execute("SELECT DISTINCT from_entity FROM relations")
    from_entities = set(row[0] for row in cursor.fetchall())
    
    cursor.execute("SELECT DISTINCT to_entity FROM relations")
    to_entities = set(row[0] for row in cursor.fetchall())
    
    all_entities = from_entities | to_entities
    
    # 获取已存在的 entities
    cursor.execute("SELECT name FROM entities")
    existing = set(row[0] for row in cursor.fetchall())
    
    # 插入新实体
    added = 0
    for entity in all_entities:
        if entity not in existing:
            # 推断实体类型
            entity_type = 'unknown'
            cursor.execute("""
                INSERT INTO entities (name, type, importance, created_at, updated_at)
                VALUES (?, ?, 0.5, ?, ?)
            """, (entity, entity_type, datetime.now().isoformat(), datetime.now().isoformat()))
            added += 1
    
    print(f"  ✅ 提取了 {added} 个新实体")
    
    # 更新 access_count
    cursor.execute("""
        UPDATE entities 
        SET access_count = (
            SELECT COUNT(*) FROM relations 
            WHERE from_entity = entities.name OR to_entity = entities.name
        )
    """)
    
    print(f"  ✅ 更新了实体的访问计数")
    
    return added

def verify_data_integrity(cursor):
    """验证数据完整性"""
    print("\n" + "=" * 60)
    print("🔍 验证数据完整性")
    print("=" * 60)
    
    issues = []
    
    # 检查 facts 和 memory_strength 的对应
    cursor.execute("SELECT COUNT(*) FROM facts")
    facts_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM memory_strength WHERE memory_type = 'fact'")
    ms_facts_count = cursor.fetchone()[0]
    
    if facts_count != ms_facts_count:
        issues.append(f"facts ({facts_count}) 与 memory_strength.fact ({ms_facts_count}) 数量不匹配")
    else:
        print(f"  ✅ facts 和 memory_strength 完整匹配: {facts_count} 条")
    
    # 检查 experiences 和 memory_strength 的对应
    cursor.execute("SELECT COUNT(*) FROM experiences")
    exp_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM memory_strength WHERE memory_type = 'experience'")
    ms_exp_count = cursor.fetchone()[0]
    
    if exp_count != ms_exp_count:
        issues.append(f"experiences ({exp_count}) 与 memory_strength.experience ({ms_exp_count}) 数量不匹配")
    else:
        print(f"  ✅ experiences 和 memory_strength 完整匹配: {exp_count} 条")
    
    # 检查 relations 的实体是否都有对应 entities 记录
    cursor.execute("SELECT DISTINCT from_entity FROM relations")
    from_entities = set(row[0] for row in cursor.fetchall())
    
    cursor.execute("SELECT DISTINCT to_entity FROM relations")
    to_entities = set(row[0] for row in cursor.fetchall())
    
    cursor.execute("SELECT name FROM entities")
    existing_entities = set(row[0] for row in cursor.fetchall())
    
    missing_entities = (from_entities | to_entities) - existing_entities
    if missing_entities:
        issues.append(f"有 {len(missing_entities)} 个关系实体没有对应的 entities 记录")
    else:
        print(f"  ✅ 所有关系实体都有对应的 entities 记录: {len(existing_entities)} 个")
    
    return issues

def print_final_stats(cursor):
    """打印最终统计"""
    print("\n" + "=" * 60)
    print("📊 最终统计")
    print("=" * 60)
    
    stats = get_stats(cursor)
    
    print(f"\n  📝 事实记忆 (facts): {stats.get('facts', 'N/A')} 条")
    print(f"  📚 经验教训 (experiences): {stats.get('experiences', 'N/A')} 条")
    print(f"  🔗 实体关系 (relations): {stats.get('relations', 'N/A')} 条")
    print(f"  👤 实体 (entities): {stats.get('entities', 'N/A')} 个")
    print(f"  💪 强度记录 (memory_strength): {stats.get('memory_strength', 'N/A')} 条")
    print(f"  🎯 情境记忆 (contexts): {stats.get('contexts', 'N/A')} 条")
    print(f"  🔗 情境绑定 (memory_context_bindings): {stats.get('memory_context_bindings', 'N/A')} 条")
    
    # 表数量
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    table_count = cursor.fetchone()[0]
    print(f"\n  📋 表总数: {table_count} 个")

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 MemoryCoreClaw 数据库优化 - 方案C")
    print("=" * 60)
    
    # 备份
    backup_path = backup_database()
    
    # 连接数据库
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # 打印初始统计
    print("\n📊 优化前统计:")
    stats_before = get_stats(cursor)
    for k, v in stats_before.items():
        if v != 'N/A':
            print(f"  {k}: {v}")
    
    try:
        # 1. 清理空表
        dropped = clean_empty_tables(cursor)
        
        # 2. 补充 memory_strength
        added = fix_memory_strength(cursor)
        
        # 3. 提取 entities
        entities_added = extract_entities_from_relations(cursor)
        
        # 4. 验证完整性
        issues = verify_data_integrity(cursor)
        
        # 提交更改
        conn.commit()
        
        # 打印最终统计
        print_final_stats(cursor)
        
        if issues:
            print("\n⚠️ 发现问题:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✅ 所有检查通过，数据完整!")
        
        print(f"\n💾 备份文件: {backup_path}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 发生错误，已回滚: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()