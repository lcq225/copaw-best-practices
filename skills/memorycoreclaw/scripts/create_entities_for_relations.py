"""
为孤立关系自动创建缺失的实体
用途：完善关系网络，让孤立关系有对应的实体定义

使用方式：
1. 先运行 check_memory.py 查看待完善关系
2. 运行本脚本预览将要创建的实体
3. 确认后输入 'y' 执行创建

命令行参数：
  python create_entities_for_relations.py --auto  # 自动创建全部，无需确认
  python create_entities_for_relations.py         # 交互式确认
"""
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = r"D:\CoPaw\.copaw\.agent-memory\memory.db"

# 常见实体类型映射
ENTITY_TYPE_HINTS = {
    # 项目/软件
    "channel": "project",
    "api": "project",
    "engine": "project",
    "system": "project",
    "core": "project",

    # 人
    "Mr": "person",
    "Ms": "person",
    "Mrs": "person",

    # 平台
    "GitHub": "platform",
    "PyPI": "platform",
    "npm": "platform",

    # 版本号
    "v1": "version",
    "v2": "version",
    "PR": "milestone",
}

def guess_entity_type(name):
    """根据名称猜测实体类型"""
    name_lower = name.lower()

    for hint, etype in ENTITY_TYPE_HINTS.items():
        if hint.lower() in name_lower:
            return etype

    # 默认类型
    if name.startswith("v") and "." in name:
        return "version"
    if name.startswith("PR"):
        return "milestone"

    return "entity"

def get_orphan_entities():
    """获取孤立关系中的实体"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 获取所有关系中的实体
    from_entities = cursor.execute('SELECT DISTINCT from_entity FROM relations').fetchall()
    to_entities = cursor.execute('SELECT DISTINCT to_entity FROM relations').fetchall()

    all_entities = set(e[0] for e in from_entities + to_entities)

    # 获取已定义的实体
    defined = cursor.execute('SELECT name FROM entities').fetchall()
    defined_names = set(e[0] for e in defined)

    # 找出未定义的实体
    undefined = all_entities - defined_names

    conn.close()
    return undefined

def preview_entities(entities):
    """预览将要创建的实体"""
    print("\n【预览】将要创建的实体：")
    print("-" * 50)

    for name in sorted(entities):
        etype = guess_entity_type(name)
        print(f"  • {name:30} → 类型: {etype}")

    print("-" * 50)
    print(f"共 {len(entities)} 个实体")

def create_entities(entities):
    """创建实体"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    created = 0
    for name in entities:
        etype = guess_entity_type(name)
        try:
            cursor.execute('''
                INSERT INTO entities (name, type, importance, created_at)
                VALUES (?, ?, ?, ?)
            ''', (name, etype, 0.5, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            created += 1
        except sqlite3.IntegrityError:
            print(f"  ⚠️ 实体已存在: {name}")

    conn.commit()
    conn.close()
    return created

def main():
    print("=" * 60)
    print("🔗 为孤立关系创建缺失实体")
    print("=" * 60)

    # 检查命令行参数
    auto_mode = "--auto" in sys.argv or "-y" in sys.argv

    # 获取孤立实体
    undefined = get_orphan_entities()

    if not undefined:
        print("\n✅ 所有关系的实体都已定义，无需处理")
        return True

    # 预览
    preview_entities(undefined)

    # 自动模式
    if auto_mode:
        print("\n[自动模式] 直接创建全部实体...")
        created = create_entities(undefined)
        print(f"\n✅ 已创建 {created} 个实体")
        
        # 验证
        remaining = get_orphan_entities()
        if not remaining:
            print("✅ 所有关系现在都有对应的实体定义")
        else:
            print(f"⚠️ 仍有 {len(remaining)} 个实体未定义")
        return True

    # 交互模式
    print("\n是否创建这些实体？")
    print("  y - 创建全部")
    print("  n - 取消")
    print("  s - 选择性创建")

    choice = input("\n请选择 [y/n/s]: ").strip().lower()

    if choice == 'y':
        created = create_entities(undefined)
        print(f"\n✅ 已创建 {created} 个实体")

        # 验证
        remaining = get_orphan_entities()
        if not remaining:
            print("✅ 所有关系现在都有对应的实体定义")
        else:
            print(f"⚠️ 仍有 {len(remaining)} 个实体未定义")

    elif choice == 's':
        print("\n选择性创建（输入实体名称，多个用逗号分隔）：")
        selected = input("实体: ").strip()
        if selected:
            names = [n.strip() for n in selected.split(',') if n.strip() in undefined]
            if names:
                created = create_entities(names)
                print(f"\n✅ 已创建 {created} 个实体")
            else:
                print("⚠️ 未找到有效实体名称")
    else:
        print("\n已取消")

    print("=" * 60)
    return True

if __name__ == "__main__":
    main()