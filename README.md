# CoPaw Best Practices

> 🚀 企业级 CoPaw 实践经验汇总 — 从单 Agent 到多 Agent 团队治理

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CoPaw](https://img.shields.io/badge/CoPaw->=0.1.0-blue.svg)](https://github.com/agentscope-ai/CoPaw)

## 📖 这是什么？

本仓库汇总了 CoPaw 在实际企业环境中的实践经验，特别是 **v0.0.7（单Agent）→ v0.1.0（多Agent）升级迁移** 过程中积累的宝贵经验。

官方文档侧重功能介绍，而这里侧重：
- ⚠️ 升级风险管理与应急恢复
- 🏢 多 Agent 团队治理机制
- 🔧 技能共享与复用最佳实践
- 🧠 记忆系统深度定制

## 🎯 适用人群

- CoPaw 企业用户
- 从旧版本升级的用户
- 需要管理多个 Agent 的团队
- 希望深度定制 CoPaw 的开发者

## 📚 内容概览

### 核心文档

| 文档 | 说明 | 推荐 |
|------|------|------|
| [升级应急手册](docs/upgrade-playbook.md) | 升级前备份 + 危机恢复流程 | ⭐⭐⭐⭐⭐ |
| [Agent 团队治理](docs/agent-management.md) | 身份认证 + 红线准则 + 惩罚机制 | ⭐⭐⭐⭐⭐ |
| [安全最佳实践](docs/security-best-practices.md) | 权限管理 + 敏感信息脱敏 | ⭐⭐⭐⭐⭐ |
| [记忆系统最佳实践](docs/memory-system-best-practices.md) | 决策生命周期 + 可信度分层 + 向量搜索 + **记忆提取** + **压缩前刷新** | ⭐⭐⭐⭐⭐ 2026-03-31 |
| [上下文保存系统](docs/context-flush-best-practices.md) | 三层保存体系 + 会话快照 + 操作跟踪 + 压缩保护 | ⭐⭐⭐⭐⭐ NEW 2026-03-31 |
| [CoPaw 升级与记忆系统增强](docs/copaw-upgrade-summary-20260331.md) | v1.0.0 升级修复 + 业界领先记忆功能 | ⭐⭐⭐⭐⭐ NEW |
| [CoPaw 使用技巧](docs/copaw-usage-tips.md) | 日常使用技巧 + 常见问题解答 | ⭐⭐⭐⭐ |
| [技能共享机制](docs/skill-sharing.md) | 全局/局部技能划分 + 继承规则 | ⭐⭐⭐⭐ |
| [GitHub 工作流规范](docs/github-workflow.md) | Fork/PR 流程 + 提交规范 | ⭐⭐⭐⭐ |
| [v0.0.7 → v0.1.0 迁移指南](docs/migration-v0.0.7-to-v0.1.0.md) | 单Agent到多Agent的实战迁移 | ⭐⭐⭐⭐ |

### 部署指南

| 文档 | 说明 |
|------|------|
| [Windows 环境最佳实践](docs/windows-best-practices.md) | 编码问题 + 路径处理 + SSL |
| [Ollama 本地部署](docs/ollama-local-deployment.md) | 本地 LLM + Embedding 配置 |
| [企业微信接入](docs/wecom-integration.md) | 智能机器人 vs 企业应用对比 |

### 工具脚本

| 脚本 | 用途 |
|------|------|
| [upgrade_backup.ps1](scripts/upgrade_backup.ps1) | 一键备份/验证/恢复 CoPaw 关键文件 |

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
| [Meta-Harness](skills/meta-harness/) | Agent 输出质量评估与经验回溯系统 |

## 🚀 快速开始

### 升级前备份（强烈推荐）

```powershell
# 下载脚本
# 在 CoPaw 根目录执行
.\scripts\upgrade_backup.ps1 -Action backup
```

### 验证当前状态

```powershell
.\scripts\upgrade_backup.ps1 -Action verify
```

### 创建新 Agent

```powershell
# 复制模板到新 Agent 工作区
cp templates/* .copaw/workspaces/your-new-agent/
```

## 💡 核心经验总结

### 1. 升级风险意识

> **问题：** CoPaw 原地 update 升级可能导致架构紊乱

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
- 全局技能：所有 Agent 共享
- 局部技能：Agent 特有
- 继承规则：局部优先 → 全局兜底

### 4. 记忆系统

> **问题：** 默认记忆系统功能有限

**方案：** MemoryCoreClaw 技能
- 事实记忆：存储知识点
- 教训记忆：避免重复犯错
- 关系记忆：记住人和事

### 5. Agent 质量保障

> **问题：** 如何评估 Agent 输出质量？经验如何复用？

**方案：** Meta-Harness 系统
- 自动评估：多维度评分（正确性/完整性/效率/安全性等）
- 经验存储：SQLite 结构化存储所有任务
- 智能索引：高/低分经验自动存记忆系统
- 统计查询：成功率、工具效果分析

## 🤝 贡献

欢迎分享你的 CoPaw 实践经验！

1. Fork 本仓库
2. 创建你的分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建 Pull Request

## 📄 许可证

[MIT License](LICENSE)

## 🔗 相关链接

- [CoPaw 官方仓库](https://github.com/agentscope-ai/CoPaw)
- [CoPaw 官方文档](https://github.com/agentscope-ai/CoPaw#readme)
- [AgentScope 框架](https://github.com/agentscope-ai/agentscope)

---

⭐ 如果这个仓库对你有帮助，欢迎 Star！