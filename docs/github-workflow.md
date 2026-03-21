# GitHub 工作流规范

> **版本：** 1.0
> **用途：** CoPaw 相关项目的 GitHub 开发流程规范

---

## 一、项目目录规范

### 统一存放位置

```
D:\github\
├── CoPaw\           # 官方仓库 Fork
├── agentscope\      # 其他相关项目
└── your-project\    # 你的项目
```

**规则：**
- 所有 GitHub 项目统一存放在 `D:\github\` 目录
- 目录名与仓库名一致
- 不要随意创建目录

---

## 二、Fork → Clone → Upstream 工作流

### 流程图

```
upstream (官方仓库)
agentscope-ai/CoPaw
      │
      │ 1. Fork 到自己账户
      ▼
origin (用户 Fork)
lcq225/CoPaw
      │
      │ 2. Clone 到本地
      ▼
local (本地仓库)
D:\github\CoPaw\

3. 配置 upstream: git remote add upstream <官方仓库URL>
```

### 操作步骤

```bash
# 1. Clone 自己的 Fork
git clone https://github.com/your-username/CoPaw.git
cd CoPaw

# 2. 配置 upstream
git remote add upstream https://github.com/agentscope-ai/CoPaw.git

# 3. 验证配置
git remote -v
# origin    https://github.com/your-username/CoPaw.git (fetch)
# origin    https://github.com/your-username/CoPaw.git (push)
# upstream  https://github.com/agentscope-ai/CoPaw.git (fetch)
# upstream  https://github.com/agentscope-ai/CoPaw.git (push)
```

---

## 三、日常开发流程

### 同步上游更新

```bash
# 1. 获取上游更新
git fetch upstream

# 2. 切换到主分支
git checkout main

# 3. 合并上游更新
git merge upstream/main

# 4. 推送到自己的 Fork
git push origin main
```

### 创建功能分支

```bash
# 1. 从最新的 main 创建分支
git checkout -b feature/your-feature

# 2. 开发、提交
git add .
git commit -m "feat: your feature description"

# 3. 推送到 Fork
git push origin feature/your-feature

# 4. 在 GitHub 网页创建 PR
```

---

## 四、PR 提交前检查清单

### 必做检查

```
□ Fork 是否已同步最新代码？
□ 是否在 Issue 下评论认领任务？
□ 本地是否运行了格式检查？
□ 本地是否运行了测试？
□ 提交信息是否符合规范？
□ 是否检查了敏感信息脱敏？
```

### 格式检查命令

```bash
# website 目录
cd website
pnpm run format:check  # 检查
pnpm run format        # 自动修复

# console 目录
cd console
npm run format:check   # 检查
npm run format         # 自动修复

# pre-commit 检查
pre-commit run --all-files
```

---

## 五、提交信息规范

### Conventional Commits

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| Type | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 Bug |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响功能） |
| `refactor` | 重构 |
| `test` | 测试相关 |
| `chore` | 构建/工具相关 |

### 示例

```bash
# 好的提交信息
git commit -m "feat(memory): add semantic search support"
git commit -m "fix(windows): resolve GBK encoding issue"
git commit -m "docs: update installation guide"

# 不好的提交信息
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

---

## 六、常见 CI 失败原因

### Prettier 格式检查

**错误：** `format check failed`

**解决：**
```bash
cd website && pnpm run format
cd console && npm run format
```

### Pre-commit 检查

**错误：** `trailing-whitespace`, `end-of-file-fixer`

**解决：**
```bash
# 自动修复
pre-commit run --all-files

# 修复后重新提交
git add -A
git commit -m "style: fix pre-commit issues"
```

### 关键教训

1. **pre-commit 会自动修复文件**，修复后必须重新 commit
2. **trailing-whitespace 是最常见问题**，markdown 文件容易有多余空格
3. **本地检查通过 ≠ CI 通过**，确保本地环境与 CI 一致

---

## 七、敏感信息脱敏

### 检查清单

```
□ 是否包含 API Key / Token / 密码？
□ 是否包含个人隐私信息？
□ 是否包含内网地址或敏感配置？
□ 是否包含真实文件路径？
□ 代码示例中的配置是否使用占位符？
```

### 脱敏示例

```json
// ❌ 错误（泄露敏感信息）
{
  "api_key": "tvly-dev-3bSZY4-xxx"
}

// ✅ 正确（使用占位符）
{
  "api_key": "your-api-key-here"
}
```

---

## 八、Issue 认领流程

### 流程

1. 检查 Issue 是否开放/未分配
2. 评论认领：「我想认领 Task #XX，准备提交 PR」
3. **等待维护者确认后再开始工作**
4. 定期检查是否有人已提交相同 PR

### 教训

> 不要急于动手，先确认任务状态！

---

## 九、回答 Issue 原则

### 回答前必做

| 步骤 | 内容 |
|------|------|
| 1 | 搜索相关 Issue |
| 2 | 查看 PR 讨论 |
| 3 | 阅读源码/文档 |
| 4 | 参考其他人的回答风格 |

### 切忌

- ❌ 冲动回答
- ❌ 猜测
- ❌ 只给临时方案

---

## 相关文档

- [升级应急手册](upgrade-playbook.md)
- [Windows 环境最佳实践](windows-best-practices.md)