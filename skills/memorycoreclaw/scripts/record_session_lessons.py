"""
记录会话关键经验到记忆数据库

使用方法:
1. 修改下面的示例内容为你想要记录的经验教训
2. 运行脚本: python record_session_lessons.py [数据库路径]
   或设置环境变量: set MEMORY_DB_PATH=你的路径
"""
import sys
import os

# 添加模块路径（scripts 目录 -> memorycoreclaw -> active_skills）
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(script_dir)))

from memorycoreclaw import Memory

# 数据库路径
def get_db_path():
    if 'MEMORY_DB_PATH' in os.environ:
        return os.environ['MEMORY_DB_PATH']
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.path.join(os.getcwd(), '.copaw', '.agent-memory', 'memory.db')

mem = Memory(db_path=get_db_path())

# ============================================================
# 示例：记录经验教训
# ============================================================

# 示例 1: 记录负面经验（教训）
# mem.learn(
#     action="描述你做了什么",
#     context="描述当时的情境",
#     outcome="negative",  # 或 "positive"
#     insight="描述你学到了什么",
#     importance=0.85  # 0-1 之间，越高越重要
# )

# 示例 2: 记录事实信息
# mem.remember(
#     "描述你想记住的事实",
#     importance=0.6,
#     category="config"  # 可选：config, lesson, fact, relation 等
# )

# 示例 3: 记录关系
# mem.relate(
#     subject="主体",
#     relation="关系类型",
#     obj="客体",
#     properties={"额外信息": "值"}
# )

# ============================================================
# 在这里添加你想要记录的内容
# ============================================================

# 你的记录代码...

print("经验教训已记录到记忆数据库")