# QwenPaw Best Practices

> 🚀 企业级 QwenPaw 实践经验汇总 — 从单 Agent 到多 Agent 团队治理

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![QwenPaw](https://img.shields.io/badge/QwenPaw-v1.1.x-blue.svg)](https://github.com/agentscope-ai/QwenPaw)

## 📖 这是什么？

本仓库汇总了 QwenPaw 在实际企业环境中的实践经验，特别是版本升级迁移过程中积累的宝贵经验。

官方文档侧重功能介绍，而这里侧重：
- ⚠️ 升级风险管理与应急恢复
- 🏢 多 Agent 团队治理机制
- 🔧 技能共享与复用最佳实践
- 🧠 记忆系统深度定制

## 🎯 适用人群

- QwenPaw 企业用户
- 从旧版本升级的用户
- 需要管理多个 Agent 的团队
- 希望深度定制 QwenPaw 的开发者

## 📚 内容概览

### 核心文档

| 文档 | 说明 | 推荐 |
|------|------|------|
| [升级应急手册](docs/upgrade-playbook.md) | 升级前备份 + 危机恢复流程 | ⭐⭐⭐⭐⭐ |
| [Agent 团队治理](docs/agent-management.md) | 身份认证 + 红线准则 + 惩罚机制 | ⭐⭐⭐⭐⭐ |
| [安全最佳实践](docs/security-best-practices.md) | 权限管理 + 敏感信息脱敏 | ⭐⭐⭐⭐⭐ |
| [记忆系统最佳实践](docs/memory-system-best-practices.md) | 决策生命周期 + 可信度分层 + 向量搜索 | ⭐⭐⭐⭐⭐ |
| [上下文保存系统](docs/context-flush-best-practices.md) | 三层保存体系 + 会话快照 + 操作跟踪 | ⭐⭐⭐⭐⭐ |
| [Windows 环境最佳实践](docs/windows-best-practices.md) | 编码问题 + 路径处理 + SSL | ⭐⭐⭐⭐⭐ |
| [技能共享机制](docs/skill-sharing.md) | 全局/局部技能划分 + 继承规则 | ⭐⭐⭐⭐ |
| [GitHub 工作流规范](docs/github-workflow.md) | Fork/PR 流程 + 提交规范 | ⭐⭐⭐⭐ |

### 部署指南

| 文档 | 说明 |
|------|------|
| [Ollama 本地部署](docs/ollama-local-deployment.md) | 本地 LLM + Embedding 配置 |
| [企业微信接入](docs/wecom-integration.md) | 智能机器人 vs 企业应用对比 |

### 工具脚本

| 脚本 | 用途 |
|------|------|
| [upgrade_backup.ps1](scripts/upgrade_backup.ps1) | 一键备份/验证/恢复 QwenPaw 关键文件 |

### 模板文件

| 模板 | 说明 |
|------|------|
| [AGENTS.md](templates/AGENTS.md) | Agent 行为规则模板 |
| [SOUL.md](templates/SOUL.md) | Agent 身份定义模板 |
| [PROFILE.md](templates/PROFILE.md) | 用户资料模板 |
| [MEMORY.md](templates/MEMORY.md) | 记忆摘要模板 |
| [HEARTBEAT.md](templates/HEARTBEAT.md) | 定期任务模板 |

### 高级技能

| 技能 | 说明 |
|------|------|
| [MemoryCoreClaw](skills/memorycoreclaw/) | 类人脑记忆系统，支持事实/教训/关系存储 |
| [Self-Evolution](skills/self-evolution/) | Agent 自我进化引擎，自动错误捕获与改进 |

## 🚀 快速开始

### 升级前备份（强烈推荐）

```powershell
# 下载脚本
# 在 QwenPaw 根目录执行
.\scripts\upgrade_backup.ps1 -Action backup
```

### 验证当前状态

```powershell
.\scripts\upgrade_backup.ps1 -Action verify
```

### 创建新 Agent

```powershell
# 复制模板到新 Agent 工作区
cp templates/* .qwenpaw/workspaces/your-new-agent/
```

## 💡 核心经验总结

### 1. 升级风险意识

> **问题：** QwenPaw 原地 update 升级可能导致架构紊乱

**原因：**
- 新版本架构变化与旧配置冲突
- 无备份习惯，出问题无法回滚
- 全局/局部边界不清

**解决：**
- 升级前必须备份关键文件
- 阅读官方 Release Notes
- 升级后运行检查清单

### 2. 多 Agent 治理

> **问题：** 多 Agent 环境下，如何避免混乱？

**方案：**
- 确立最高管理者身份
- 建立身份认证规则
- 定义红线准则和惩罚机制

### 3. 技能共享机制

> **问题：** 每个 Agent 都有相同技能，浪费资源

**方案：**
- 全局技能：所有 Agent 共享（`skill_pool/`）
- 局部技能：Agent 特有（`skills/`）
- 继承规则：局部优先 → 全局兜底

### 4. 记忆系统

> **问题：** 默认记忆系统功能有限

**方案：** MemoryCoreClaw 技能
- 事实记忆：存储知识点
- 教训记忆：避免重复犯错
- 关系记忆：记住人和事
- 向量搜索：语义检索

### 5. 安全防护

> **问题：** 如何防止 Agent 误操作？

**方案：** 三层防护机制
- tool_guard：工具调用审批
- file_guard：敏感文件保护
- skill_scanner：技能安全扫描

### 6. 权限分级

> **问题：** 如何平衡效率与安全？

**方案：** 5级权限模型
- default：危险操作需审批
- plan：只规划不执行
- acceptEdits：文件操作自动执行
- auto：大部分操作自动执行
- bypass：全自动执行（仅信任用户）

## 🤝 贡献

欢迎分享你的 QwenPaw 实践经验！

1. Fork 本仓库
2. 创建你的分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建 Pull Request

## 📄 许可证

[MIT License](LICENSE)

## 🔗 相关链接

- [QwenPaw 官方仓库](https://github.com/agentscope-ai/QwenPaw)
- [QwenPaw 官方文档](https://qwenpaw.agentscope.io/)
- [AgentScope 框架](https://github.com/agentscope-ai/agentscope)

---

⭐ 如果这个仓库对你有帮助，欢迎 Star！