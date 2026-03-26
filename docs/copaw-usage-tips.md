# CoPaw 使用技巧与最佳实践

> 本文档总结了 CoPaw 日常使用中的技巧、常见问题和解决方案。

## 一、环境配置

### 1.1 目录结构

```
D:\CoPaw\
├── .copaw\                    # 配置目录
│   ├── config.json            # 全局配置
│   ├── .agent-memory\         # 记忆数据库
│   ├── active_skills\         # 全局技能
│   └── workspaces\
│       ├── default\           # default Agent
│       │   ├── AGENTS.md      # Agent 行为规则
│       │   ├── MEMORY.md      # 记忆摘要
│       │   └── active_skills\ # 局部技能
│       └── SivaAgent\         # 其他 Agent
│
├── .copaw.secret\             # 敏感凭证
│   ├── github.json            # GitHub Token
│   ├── credentials.json       # Matrix 凭证
│   └── providers.json         # LLM 提供商
│
└── OB-CoPaw\                  # 输出目录
    ├── 方案\                  # 技术方案
    ├── 报告\                  # 分析报告
    ├── 笔记\                  # 学习笔记
    └── 会议记录\              # 会议纪要
```

### 1.2 Python 环境

```powershell
# 虚拟环境路径
D:\CoPaw\copaw-env\Scripts\python.exe

# 激活环境
D:\CoPaw\copaw-env\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 1.3 敏感凭证管理

```json
// .copaw.secret/providers.json
{
  "providers": [
    {
      "id": "openai",
      "api_key": "sk-xxx",
      "base_url": "https://api.openai.com/v1"
    },
    {
      "id": "deepseek",
      "api_key": "sk-xxx",
      "base_url": "https://api.deepseek.com/v1"
    }
  ]
}
```

---

## 二、记忆系统使用

### 2.1 分层记忆原则

| 层级 | 内容 | 更新频率 |
|------|------|----------|
| MEMORY.md | 精简要点、核心身份 | 每周更新 |
| memory.db | 详细内容、向量搜索 | 实时更新 |
| memory/*.md | 每日笔记、会议记录 | 每日更新 |

### 2.2 记忆写入最佳实践

```python
# 重要决策 → 记录原因
mem.remember_decision(
    decision="选择 PostgreSQL 作为主数据库",
    reason="支持复杂查询、JSON 类型、高并发",
    source="user",
)

# 经验教训 → 记录完整上下文
mem.learn(
    action="未备份直接修改配置文件",
    context="修改 config.json 前没有备份",
    outcome="negative",
    insight="修改配置文件前必须备份，保留最近3次备份",
    importance=0.9
)

# 用户偏好 → 记录重要性和分类
mem.remember(
    content="用户偏好 BLUF 沟通风格（结论先行）",
    importance=0.85,
    category="preference"
)
```

### 2.3 记忆检索技巧

```python
# 关键词搜索
results = mem.recall("压缩模型", limit=5)

# 按分类搜索
preferences = mem.recall_by_category("preference")

# 按重要性筛选
important = mem.recall_by_importance(min_importance=0.8)

# 实体关系搜索
network = mem.associate("Mr Lee", depth=1)
```

---

## 三、技能管理

### 3.1 技能目录结构

```
active_skills/
├── memorycoreclaw/           # 记忆系统
│   ├── SKILL.md              # 技能文档
│   ├── core/                 # 核心代码
│   └── scripts/              # 工具脚本
├── self_evolution/           # 自我进化
├── docx/                     # Word 文档处理
├── pdf/                      # PDF 处理
└── ...
```

### 3.2 使用技能

```python
# 读取技能文档
skill_doc = read_file("active_skills/memorycoreclaw/SKILL.md")

# 导入技能模块
from memorycoreclaw import Memory

# 使用技能功能
mem = Memory(db_path="path/to/memory.db")
```

### 3.3 技能同步工具

```bash
# 比较全局和局部技能版本
python D:\CoPaw\.copaw\scripts\custom\skill_sync.py compare

# 同步最佳版本
python D:\CoPaw\.copaw\scripts\custom\skill_sync.py sync
```

---

## 四、GitHub 工作流

### 4.1 优先使用 gh CLI

```bash
# 创建 Issue
gh issue create --repo owner/repo --title "标题" --body "内容" --label bug

# 查看 Issue 列表
gh issue list --repo owner/repo

# 创建 PR
gh pr create --repo owner/repo --title "标题" --body "内容"

# 查看仓库信息
gh repo view owner/repo
```

### 4.2 Fork → Clone → upstream 工作流

```bash
# 1. Fork 到自己账户（网页操作）

# 2. Clone 到本地
git clone https://github.com/lcq225/CoPaw.git D:\github\CoPaw

# 3. 配置 upstream
git remote add upstream https://github.com/agentscope-ai/CoPaw.git

# 4. 日常同步
git fetch upstream
git checkout main
git merge upstream/main
git push origin main

# 5. 创建功能分支
git checkout -b feature/xxx

# 6. 开发完成后推送
git push origin feature/xxx

# 7. 创建 PR（网页或 gh CLI）
gh pr create --repo agentscope-ai/CoPaw --title "feat: xxx"
```

### 4.3 PR 提交前检查

```bash
# 运行格式检查
cd website && pnpm run format:check
cd console && npm run format:check

# 运行 pre-commit
pre-commit run --all-files

# 如果有自动修复，重新提交
git add -A
git commit -m "style: fix pre-commit issues"
```

---

## 五、定时任务管理

### 5.1 创建定时任务

```bash
# 每天 9:00 发送文本消息
copaw cron create \
  --type text \
  --name "每日提醒" \
  --cron "0 9 * * *" \
  --channel console \
  --target-user default \
  --target-session default \
  --text "早上好！新的一天开始了。"

# 每 2 小时向 Agent 提问
copaw cron create \
  --type agent \
  --name "检查待办" \
  --cron "0 */2 * * *" \
  --channel console \
  --target-user default \
  --target-session default \
  --text "我有什么待办事项？"
```

### 5.2 管理定时任务

```bash
# 列出所有任务
copaw cron list

# 查看任务详情
copaw cron get <job_id>

# 暂停/恢复任务
copaw cron pause <job_id>
copaw cron resume <job_id>

# 删除任务
copaw cron delete <job_id>

# 立即执行一次
copaw cron run <job_id>
```

### 5.3 Cron 表达式示例

```
0 9 * * *      # 每天 9:00
0 */2 * * *    # 每 2 小时
30 8 * * 1-5   # 工作日 8:30
0 0 * * 0      # 每周日零点
*/15 * * * *   # 每 15 分钟
0 3 * * 0      # 每周日凌晨3点
```

---

## 六、Windows 编码处理

### 6.1 常见问题

Windows 中文环境下默认使用 GBK 编码，处理 emoji 或特殊 Unicode 字符时会报错。

### 6.2 解决方案

```python
# Python 脚本开头添加
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 文件读写指定编码
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 环境变量设置
$env:PYTHONIOENCODING = "utf-8"
chcp 65001  # 切换控制台为 UTF-8
```

### 6.3 模块导入规范

```python
# ❌ 错误：库模块在模块级别包装 stdout
# utils.py
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ✅ 正确：库模块不包装，让调用者决定
# utils.py
def my_function():
    pass  # 不包装 stdout

# main.py（主脚本）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from utils import my_function  # 安全导入
```

---

## 七、文档输出规范

### 7.1 目录结构

```
D:\CoPaw\OB-CoPaw\
├── 方案\        # 技术方案、解决方案、实施计划
├── 报告\        # 分析报告、调研报告、总结报告
├── 笔记\        # 学习笔记、知识整理、备忘记录
└── 会议记录\    # 会议纪要、讨论记录
```

### 7.2 命名规范

```
格式：YYYY-MM-DD_标题.md

示例：
- 2026-03-26_记忆系统增强方案.md
- 2026-03-26_月度运维报告.md
- 2026-03-26_Python异步编程笔记.md
```

### 7.3 长文档输出原则

```markdown
1. 使用 write_file 一次性写入，不分段追加
2. 给用户进度反馈："文档已生成，共X行"
3. 完成后验证结构（抽查章节是否重复）
4. 禁止用 edit_file 追加大段内容（会重复）
5. 禁止依赖终端输出长内容（会中断）
```

---

## 八、安全最佳实践

### 8.1 敏感信息脱敏

| 敏感类型 | 示例 | 处理方式 |
|---------|------|---------|
| API Key | `tvly-dev-xxx` | 替换为 `your-api-key` |
| Token | `ghp_xxx` | 替换为 `your-token` |
| 密码 | 任何密码 | 完全删除或 `***` |
| 个人信息 | 手机号、邮箱 | 脱敏处理 |
| 内网地址 | `192.168.x.x` | 替换为 `your-server` |

### 8.2 权限控制

```python
# 检查用户权限
if channel not in ['console', 'wecom:HI2044']:
    return "抱歉，您没有权限执行此操作。"
```

### 8.3 外发操作授权

```
禁止自动执行的外发操作：
- 创建 PR、push 代码
- 发布 Issue、评论
- 发送邮件、消息
- 上传文件到公开平台

正确做法：
1. 准备好内容/操作 → 向用户展示预览
2. 等待用户明确指令
3. 收到指令后再执行
```

---

## 九、常见问题

### Q1: Agent 不记得之前的内容？

**原因：** 每次会话是全新的，需要通过记忆系统恢复上下文

**解决：**
1. 确保关键信息写入 memory.db
2. 会话开始时检查 MEMORY.md 和记忆数据库
3. 使用 `mem.recall()` 搜索历史记忆

### Q2: 技能不生效？

**检查：**
1. 技能是否在 `active_skills/` 目录
2. SKILL.md 是否存在
3. 技能描述是否清晰

### Q3: 压缩功能异常？

**可能原因：**
1. ReActAgent 注入干扰
2. 压缩模型配置错误
3. 提示词格式问题

**解决：** 使用 DirectCompactor 绕过 ReActAgent

### Q4: 数据库锁定？

**解决：**
```bash
# 检查是否有其他进程占用
# 删除锁定文件
del "memory.db-journal"
del "memory.db-wal"
```

---

## 十、参考资源

- [CoPaw 官方仓库](https://github.com/agentscope-ai/CoPaw)
- [CoPaw 文档](https://agentscope-ai.github.io/CoPaw/)
- [记忆系统最佳实践](./memory-system-best-practices.md)
- [安全最佳实践](./security-best-practices.md)