"""
记忆系统自动检查 - 支持启动时检查
功能：
1. 检查上次检查时间
2. 如果超过7天，自动执行检查
3. 更新检查时间记录
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# 路径配置
SCRIPT_DIR = Path(__file__).parent
LAST_CHECK_FILE = SCRIPT_DIR / "last_check.json"
CHECK_INTERVAL_DAYS = 7

def get_last_check_time():
    """获取上次检查时间"""
    if LAST_CHECK_FILE.exists():
        with open(LAST_CHECK_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return datetime.fromisoformat(data.get('last_check_time', '2000-01-01'))
    return datetime(2000, 1, 1)

def update_check_time():
    """更新检查时间"""
    now = datetime.now()
    next_check = now + timedelta(days=CHECK_INTERVAL_DAYS)

    data = {
        'last_check_time': now.isoformat(),
        'check_interval_days': CHECK_INTERVAL_DAYS,
        'next_check_time': next_check.replace(hour=9, minute=30, second=0).isoformat()
    }

    with open(LAST_CHECK_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def should_check():
    """判断是否需要检查"""
    last_check = get_last_check_time()
    now = datetime.now()
    days_since_check = (now - last_check).days
    return days_since_check >= CHECK_INTERVAL_DAYS

def run_check():
    """执行记忆检查"""
    print("=" * 60)
    print("🔄 自动记忆检查")
    print("=" * 60)

    # 导入并执行检查
    from check_memory import check_memory
    result = check_memory()

    # 更新检查时间
    update_check_time()

    print("\n✅ 检查完成，下次检查时间: 7天后")
    return result

def startup_check():
    """启动时检查入口"""
    if should_check():
        print("\n⏰ 距离上次检查已超过7天，执行自动检查...")
        return run_check()
    else:
        last_check = get_last_check_time()
        days_left = CHECK_INTERVAL_DAYS - (datetime.now() - last_check).days
        print(f"\n📅 上次检查: {last_check.strftime('%Y-%m-%d %H:%M')}")
        print(f"   距下次检查还有 {days_left} 天")
        return None

if __name__ == "__main__":
    startup_check()