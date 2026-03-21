# v0.0.7 → v0.1.0 迁移指南

> **从单 Agent 到多 Agent 的实战经验**

---

## 一、版本差异

| 特性 | v0.0.7 | v0.1.0 |
|------|--------|--------|
| Agent 数量 | 单 Agent | 多 Agent |
| 工作区结构 | 单一工作区 | `workspaces/` 目录 |
| 技能位置 | `active_skills/` | 全局 + 局部 |
| 记忆共享 | 不涉及 | 多 Agent 共享 |
| 身份认证 | 无 | 需要考虑 |

---

## 二、迁移前准备

### 备份（必须！）

```powershell
# 使用备份脚本
.\scripts\upgrade_backup.ps1 -Action backup

# 或手动备份
$backupPath = "D:\Backup\copaw_before_migration_$(Get-Date -Format 'yyyyMMdd')"
$copawPath = "你的CoPaw路径\.copaw"

Copy-Item "$copawPath\.agent-memory\memory.db" "$backupPath\memory.db" -Force
Copy-Item "$copawPath\config.json" "$backupPath\config.json" -Force
Copy-Item "$copawPath\workspaces\default\*.md" "$backupPath\" -Force
```

### 记录当前状态

```powershell
# 记录当前技能列表
dir /b "$copawPath\active_skills" > "$backupPath\skills_before.txt"

# 记录当前配置
type "$copawPath\config.json" > "$backupPath\config_before.txt"
```

---

## 三、迁移步骤

### 步骤 1：执行升级

```powershell
# 按官方指南执行 update
# 具体命令参考 CoPaw 官方文档
```

### 步骤 2：检查目录结构

升级后应该看到：
```
.copaw\
├── workspaces/
│   └── default/      ← 原 Agent 迁移到这里
├── active_skills/    ← 全局技能
└── .agent-memory/    ← 记忆数据库
```

### 步骤 3：梳理技能

```powershell
# 检查是否有重复技能
# 全局: .copaw\active_skills\
# 局部: .copaw\workspaces\default\active_skills\

# 如果全局和局部都有同名技能，决定保留哪个
```

**决策原则：**
- 功能相同 → 保留全局，删除局部
- 配置不同 → 保留局部（特殊需求）
- 功能不同 → 重命名区分

### 步骤 4：更新文档

创建/更新以下文档：

| 文档 | 内容 |
|------|------|
| `AGENT_MANAGEMENT.md` | Agent 团队治理规则 |
| `templates/` | 新 Agent 模板 |
| `AGENTS.md` | 行为规则（增加多 Agent 相关） |

### 步骤 5：验证

```
□ 记忆数据库是否正常？
□ Agent 身份是否正确？
□ 全局技能是否可用？
□ 局部技能是否可用？
□ 敏感凭证是否有效？
```

---

## 四、常见问题

### 问题 1：技能重复

**现象：** 全局和局部都有 `browser_visible` 等技能

**解决：**
```powershell
# 检查差异
diff "$copawPath\active_skills\browser_visible\SKILL.md" "$copawPath\workspaces\default\active_skills\browser_visible\SKILL.md"

# 如果相同，删除局部
Remove-Item "$copawPath\workspaces\default\active_skills\browser_visible" -Recurse -Force
```

### 问题 2：文档散乱

**现象：** 全局目录下有很多 md 文件

**解决：**
```
# 整理规则：
.copaw\
├── AGENT_MANAGEMENT.md   ← 保留（全局管理）
├── UPGRADE_PLAYBOOK.md   ← 保留（升级手册）
├── templates/            ← 保留（模板）
├── active_skills/        ← 技能
└── .agent-memory/        ← 记忆

# 其他 md 文件移到 backup/ 或删除
```

### 问题 3：记忆路径不一致

**现象：** 记忆数据库中有旧路径引用

**解决：**
```python
# 等待验证期后（建议 3-5 天），更新数据库中的路径
# 或者在 SKILL.md 中同时支持新旧路径
```

---

## 五、迁移后优化

### 建立治理机制

1. 创建 `AGENT_MANAGEMENT.md`
2. 定义身份认证规则
3. 建立红线准则

### 创建模板

```
.copaw\templates\
├── AGENTS.md      ← 行为规则模板
├── SOUL.md        ← 身份定义模板
├── PROFILE.md     ← 用户资料模板
├── MEMORY.md      ← 记忆摘要模板
└── HEARTBEAT.md   ← 定期任务模板
```

### 规划 Agent 团队

```
现有：default（主 Agent）

规划：
├── default        ← 主 Agent（管理）
├── assistant      ← 助手 Agent（日常）
└── specialist     ← 专家 Agent（特定领域）
```

---

## 六、回滚方案

如果迁移后出现严重问题：

```powershell
# 1. 停止 CoPaw

# 2. 恢复备份
$backupPath = "D:\Backup\copaw_before_migration_YYYYMMDD"
$copawPath = "你的CoPaw路径\.copaw"

Copy-Item "$backupPath\memory.db" "$copawPath\.agent-memory\memory.db" -Force
Copy-Item "$backupPath\config.json" "$copawPath\config.json" -Force
Copy-Item "$backupPath\*.md" "$copawPath\workspaces\default\" -Force

# 3. 降级到旧版本（如果有安装包）

# 4. 重启 CoPaw
```

---

## 七、经验总结

### 做对的

✅ 升级前备份
✅ 梳理技能重复
✅ 建立治理机制
✅ 创建模板

### 踩过的坑

❌ 没有提前了解新架构
❌ 技能重复导致混乱
❌ 文档散乱难以整理
❌ 记忆路径不一致

### 建议

1. **先读 Release Notes** — 了解架构变化
2. **先备份再升级** — 这是底线
3. **逐步迁移** — 不要急于创建多 Agent
4. **保持简单** — 能放全局就放全局

---

## 八、相关文档

- [升级应急手册](upgrade-playbook.md)
- [Agent 团队治理](agent-management.md)
- [技能共享机制](skill-sharing.md)