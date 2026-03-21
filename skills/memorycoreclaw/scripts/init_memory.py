"""
初始化记忆数据库并迁移 MEMORY.md 内容
"""

import sys
import os

# 添加模块路径（scripts 目录 -> memorycoreclaw -> active_skills）
skill_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(skill_dir)))

from memorycoreclaw import Memory

# 数据库路径：优先使用环境变量，其次使用命令行参数，最后使用默认值
def get_db_path():
    if 'MEMORY_DB_PATH' in os.environ:
        return os.environ['MEMORY_DB_PATH']
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.path.join(os.getcwd(), '.copaw', '.agent-memory', 'memory.db')

DB_PATH = get_db_path()

def init_database():
    """初始化数据库并迁移数据"""
    
    print("=" * 60)
    print("MemoryCoreClaw 数据库初始化")
    print("=" * 60)
    print(f"\n数据库路径: {DB_PATH}\n")
    
    # 创建 Memory 实例（会自动创建数据库和表）
    mem = Memory(db_path=DB_PATH)
    
    print("✅ 数据库创建成功\n")
    
    # ========== 1. 用户核心信息 ==========
    print("📝 写入用户核心信息...")
    
    user_facts = [
        ("用户名字是 Mr Lee", 0.95, "identity"),
        ("用户年龄 43 岁", 0.85, "identity"),
        ("用户公司在山东海科化工集团", 0.95, "identity"),
        ("用户部门是卓越与智能部", 0.85, "identity"),
        ("用户职业是 IT 相关工作，负责智能化、数字化转型", 0.85, "identity"),
        ("用户偏好专业、高效、透明的工作方式", 0.8, "preference"),
        ("用户重视闭环和可追溯性", 0.8, "preference"),
        ("用户沟通风格是 BLUF（结论先行）", 0.85, "preference"),
    ]
    
    for content, importance, category in user_facts:
        mem.remember(content, importance=importance, category=category)
    
    print(f"   写入 {len(user_facts)} 条用户信息")
    
    # ========== 2. 本地环境配置 ==========
    print("📝 写入本地环境配置...")
    
    env_facts = [
        ("操作系统是 Windows 11, 2025H2", 0.7, "environment"),
        ("用户目录是 C:\\Users\\Siva", 0.8, "environment"),
        ("文档库路径是 D:\\Users\\Siva\\Documents\\OB-LCQ", 0.9, "environment"),
        ("桌面路径是 D:\\Users\\Siva\\Desktop", 0.8, "environment"),
        ("下载路径是 D:\\Users\\Siva\\Downloads", 0.7, "environment"),
        ("Node.js 版本是 v25.2.1", 0.6, "environment"),
        ("npm 全局目录是 D:\\Programs\\nodejs\\npm-global", 0.7, "environment"),
        ("Python 版本是 3.13.11", 0.6, "environment"),
        ("pyenv 安装目录是 D:\\Programs\\pyenv\\pyenv-win", 0.7, "environment"),
        ("CoPaw 虚拟环境路径是 D:\\CoPaw\\copaw-env", 0.8, "environment"),
        ("Docker 版本是 29.2.1", 0.5, "environment"),
        ("Git 版本是 2.53.0", 0.5, "environment"),
        ("CoPaw 根目录是 D:\\CoPaw", 0.8, "environment"),
        ("CoPaw 工作区是 D:\\Users\\Siva\\Documents\\OB-LCQ\\.copaw", 0.9, "environment"),
        ("CoPaw 配置文件是 D:\\Users\\Siva\\Documents\\OB-LCQ\\.copaw\\config.json", 0.85, "environment"),
        ("敏感配置目录是 .copaw.secret", 0.9, "environment"),
        ("老K输出目录是 D:\\Users\\Siva\\Documents\\OB-LCQ\\_老K输出", 0.85, "environment"),
        ("Obsidian 文档库是 D:\\Users\\Siva\\Documents\\OB-LCQ", 0.8, "environment"),
    ]
    
    for content, importance, category in env_facts:
        mem.remember(content, importance=importance, category=category)
    
    print(f"   写入 {len(env_facts)} 条环境配置")
    
    # ========== 3. 教训 ==========
    print("📝 写入经验教训...")
    
    lessons = [
        ("优先使用 GitHub API", "处理 GitHub 操作时", "positive", "GitHub API 比浏览器操作更稳定高效", 0.85),
        ("脚本开头设置 UTF-8 编码", "Windows 环境下脚本执行", "positive", "避免 GBK 编码导致的 emoji/Unicode 错误", 0.9),
        ("用户给出明确路径时严格按要求执行", "文件操作请求", "positive", "避免按默认路径查找浪费时间", 0.85),
        ("配置问题先查官方文档", "遇到配置问题时", "positive", "不要自己猜测，官方文档通常有答案", 0.8),
        ("权限检查必须在执行前完成", "收到文件操作请求时", "negative", "曾因未检查权限向未授权用户 HK05782 泄露本地文档内容", 0.95),
        ("外发操作必须获得明确授权", "PR、Issue、发布、发送消息等", "positive", "避免未经用户同意的对外操作", 0.9),
        ("敏感信息严禁对外泄露", "提交 Issue/PR/评论时", "positive", "Token、密码、后台地址、账号等信息必须脱敏", 0.95),
        ("关键文件修改前必须备份", "修改 config.json、AGENTS.md、MEMORY.md 时", "positive", "出问题可快速回滚", 0.85),
        ("临时文件用完必须删除", "使用 .copaw/temp/ 时", "positive", ".copaw 是配置目录，不是工作区", 0.75),
    ]
    
    for action, context, outcome, insight, importance in lessons:
        mem.learn(action, context, outcome, insight, importance=importance)
    
    print(f"   写入 {len(lessons)} 条教训")
    
    # ========== 4. 关系 ==========
    print("📝 写入实体关系...")
    
    relations = [
        ("Mr Lee", "works_at", "海科化工"),
        ("Mr Lee", "department", "卓越与智能部"),
        ("海科化工", "located_in", "山东东营"),
        ("CoPaw", "developed_by", "阿里云 AgentScope 团队"),
        ("MemoryCoreClaw", "developed_by", "Mr Lee"),
        ("MemoryCoreClaw", "github", "https://github.com/lcq225/MemoryCoreClaw"),
    ]
    
    for from_entity, relation, to_entity in relations:
        mem.relate(from_entity, relation, to_entity)
    
    print(f"   写入 {len(relations)} 条关系")
    
    # ========== 5. 项目信息 ==========
    print("📝 写入项目信息...")
    
    project_facts = [
        ("MemoryCoreClaw 是类人脑长期记忆引擎项目", 0.8, "project"),
        ("MemoryCoreClaw 仓库地址是 https://github.com/lcq225/MemoryCoreClaw", 0.85, "project"),
        ("MemoryCoreClaw 创建于 2026-03-19", 0.7, "project"),
        ("CoPaw PR #1601 已合并，修复 Windows GBK 编码 Bug", 0.85, "milestone"),
        ("ReMe PR #1 已合并，修复 Windows GBK 编码 Bug", 0.85, "milestone"),
        ("这是首次成功向开源项目贡献代码并被合并", 0.9, "milestone"),
    ]
    
    for content, importance, category in project_facts:
        mem.remember(content, importance=importance, category=category)
    
    print(f"   写入 {len(project_facts)} 条项目信息")
    
    # ========== 6. 用户持仓 ==========
    print("📝 写入用户持仓信息...")
    
    holdings = [
        ("用户持有股票 海科新源(301292)", 0.7, "holding"),
        ("用户持有股票 弘元绿能(603185)", 0.7, "holding"),
        ("用户持有 ETF 航天ETF(159227)", 0.7, "holding"),
        ("用户持有股票 顺丰控股(002352)", 0.7, "holding"),
        ("用户持有股票 工商银行(601398)", 0.7, "holding"),
        ("用户持有股票 乖宝宠物(301498)", 0.7, "holding"),
        ("用户持有股票 用友网络(600588)", 0.7, "holding"),
        ("用户有定时任务：每日股市分析（北京时间 08:00）", 0.75, "task"),
    ]
    
    for content, importance, category in holdings:
        mem.remember(content, importance=importance, category=category)
    
    print(f"   写入 {len(holdings)} 条持仓信息")
    
    # ========== 统计 ==========
    print("\n" + "=" * 60)
    print("📊 数据库统计")
    print("=" * 60)
    
    stats = mem.get_stats()
    print(f"""
📝 事实记忆：{stats['facts']} 条
📚 经验教训：{stats['experiences']} 条
🔗 实体关系：{stats['relations']} 条
👤 实体数量：{stats['entities']} 条
💼 工作记忆：{stats['working_memory']} 条
""")
    
    print("=" * 60)
    print("✅ 初始化完成！")
    print("=" * 60)
    
    return mem

if __name__ == "__main__":
    init_database()