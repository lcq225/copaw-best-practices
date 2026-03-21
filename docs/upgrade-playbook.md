# CoPaw 升级应急手册

> **版本：** 1.0
> **用途：** 升级时备份关键文件 + 危机时刻手工恢复

---

## 一、升级风险认知

### 问题根源
- CoPaw 从 v0.0.7（单Agent）→ v0.1.0（多Agent）
- 每次原地 update，非全新安装
- 新版本架构变化可能与旧配置冲突
- 积累的经验教训不能丢失

### 已遇到的问题
| 问题 | 表现 | 解决方式 |
|------|------|----------|
| 技能重复 | 全局和局部都有同名技能 | 删除局部，保留全局 |
| 路径迁移 | 技能路径变更 | 迁移后验证 3-5 天 |
| 文档散乱 | 全局目录 md 文件混乱 | 整理归档 |
| 配置残留 | 旧配置项未清理 | 手工清理 |

---

## 二、关键文件清单

### 🔴 核心文件（必须备份）

| 文件 | 路径 | 内容 | 恢复优先级 |
|------|------|------|------------|
| **记忆数据库** | `.copaw\.agent-memory\memory.db` | 所有记忆、教训、关系 | 🔴 最高 |
| **全局配置** | `.copaw\config.json` | 系统配置 | 🔴 最高 |
| **敏感凭证** | `.copaw.secret\` | Token、密码、API Key | 🔴 最高 |

### 🟡 Agent 核心文件（每个 Agent）

| 文件 | 内容 | 恢复优先级 |
|------|------|------------|
| **AGENTS.md** | 行为规则 | 🟡 高 |
| **SOUL.md** | 身份定义 | 🟡 高 |
| **PROFILE.md** | 用户资料 | 🟡 高 |
| **MEMORY.md** | 记忆摘要 | 🟡 高 |
| **HEARTBEAT.md** | 定期任务 | 🟡 中 |

### 🟢 可恢复文件

| 文件 | 说明 |
|------|------|
| `chats.json` | 对话历史（可丢失） |
| `sessions/` | 会话数据（可丢失） |
| `logs/` | 日志（可丢失） |

---

## 三、升级前备份流程

### 使用备份脚本（推荐）

```powershell
# 下载 scripts/upgrade_backup.ps1 到本地
# 在 CoPaw 根目录执行
.\scripts\upgrade_backup.ps1 -Action backup
```

### 手动备份命令

```powershell
# 设置路径（根据你的实际路径修改）
$backupRoot = "D:\Backup\copaw_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$copawPath = "你的CoPaw路径\.copaw"
$secretPath = "你的CoPaw路径\.copaw.secret"

# 创建备份目录
New-Item -ItemType Directory -Path $backupRoot -Force

# 1. 备份记忆数据库（最重要！）
Copy-Item "$copawPath\.agent-memory\memory.db" "$backupRoot\memory.db" -Force

# 2. 备份全局配置
Copy-Item "$copawPath\config.json" "$backupRoot\config.json" -Force

# 3. 备份敏感凭证
Copy-Item $secretPath "$backupRoot\.copaw.secret" -Recurse -Force

# 4. 备份 Agent 工作区
Copy-Item "$copawPath\workspaces\default\*.md" "$backupRoot\" -Force

# 5. 备份模板目录
Copy-Item "$copawPath\templates" "$backupRoot\templates" -Recurse -Force

Write-Host "备份完成: $backupRoot"
```

---

## 四、危机恢复流程

### 场景 1：Agent 完全失忆（记忆数据库损坏）

```powershell
# 1. 停止 CoPaw 服务

# 2. 恢复记忆数据库
$backupPath = "你的备份路径"
$copawPath = "你的CoPaw路径\.copaw"
Copy-Item "$backupPath\memory.db" "$copawPath\.agent-memory\memory.db" -Force

# 3. 重启 CoPaw
```

### 场景 2：Agent 行为异常（配置/规则损坏）

```powershell
# 恢复 Agent 核心文件
$backupPath = "你的备份路径"
$copawPath = "你的CoPaw路径\.copaw"

Copy-Item "$backupPath\AGENTS.md" "$copawPath\workspaces\default\AGENTS.md" -Force
Copy-Item "$backupPath\SOUL.md" "$copawPath\workspaces\default\SOUL.md" -Force
Copy-Item "$backupPath\PROFILE.md" "$copawPath\workspaces\default\PROFILE.md" -Force
Copy-Item "$backupPath\MEMORY.md" "$copawPath\workspaces\default\MEMORY.md" -Force
Copy-Item "$backupPath\HEARTBEAT.md" "$copawPath\workspaces\default\HEARTBEAT.md" -Force
```

### 场景 3：敏感凭证丢失

```powershell
$backupPath = "你的备份路径"
$secretPath = "你的CoPaw路径\.copaw.secret"
Copy-Item "$backupPath\.copaw.secret" $secretPath -Recurse -Force
```

### 场景 4：需要重建 Agent（最坏情况）

```powershell
# 1. 备份当前损坏状态
$copawPath = "你的CoPaw路径\.copaw"
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
Rename-Item "$copawPath\workspaces\default" "default_broken_$ts"

# 2. 创建新的工作区
New-Item -ItemType Directory -Path "$copawPath\workspaces\default" -Force

# 3. 从模板恢复
$backupPath = "你的备份路径"
Copy-Item "$backupPath\templates\*" "$copawPath\workspaces\default\" -Force

# 4. 恢复核心文件
Copy-Item "$backupPath\AGENTS.md" "$copawPath\workspaces\default\AGENTS.md" -Force
Copy-Item "$backupPath\SOUL.md" "$copawPath\workspaces\default\SOUL.md" -Force
Copy-Item "$backupPath\PROFILE.md" "$copawPath\workspaces\default\PROFILE.md" -Force
Copy-Item "$backupPath\MEMORY.md" "$copawPath\workspaces\default\MEMORY.md" -Force

# 5. 恢复记忆数据库
Copy-Item "$backupPath\memory.db" "$copawPath\.agent-memory\memory.db" -Force
```

---

## 五、升级后检查清单

```
□ 记忆数据库是否正常？
□ Agent 身份是否正确？
□ 全局技能是否可用？
□ 局部技能是否可用？
□ 记得之前的教训吗？
□ HEARTBEAT 任务是否正常？
□ 敏感凭证是否有效？（API Key、Token）
```

### 验证记忆数据库

```python
# 进入 Python 环境
import sqlite3

db_path = "你的CoPaw路径/.copaw/.agent-memory/memory.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查看记忆数量
cursor.execute("SELECT COUNT(*) FROM memories")
print(f"记忆总数: {cursor.fetchone()[0]}")

conn.close()
```

---

## 六、升级策略建议

### 升级前
1. **阅读 Release Notes** — 了解架构变化
2. **执行备份** — 使用备份脚本
3. **记录当前状态** — 截图、日志

### 升级时
1. **先在测试环境验证**（如有条件）
2. **保留旧版本回退路径**
3. **观察警告和错误信息**

### 升级后
1. **运行检查清单** — 验证核心功能
2. **对比新旧架构** — 发现不一致
3. **更新本文档** — 记录新问题

---

## 七、版本迁移记录模板

| 日期 | 原版本 | 新版本 | 变更内容 | 备份位置 |
|------|--------|--------|----------|----------|
| YYYY-MM-DD | vX.X.X | vX.X.X | 变更描述 | 备份路径 |

---

## 八、相关资源

- **CoPaw 官方文档：** https://github.com/agentscope-ai/CoPaw
- **Issue 反馈：** https://github.com/agentscope-ai/CoPaw/issues
- **备份恢复脚本：** [scripts/upgrade_backup.ps1](../scripts/upgrade_backup.ps1)

---

> **记住：** 备份是最后一道防线。升级前多花 1 分钟备份，危机时省 1 小时恢复。