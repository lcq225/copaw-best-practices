# Windows 环境最佳实践

> **版本：** 1.0
> **用途：** CoPaw 在 Windows 环境下的常见问题解决方案

---

## 一、编码问题

### 问题背景

Windows 中文环境默认使用 GBK 编码，当文件或输出包含 emoji、特殊 Unicode 字符时会出现：

```
'gbk' codec can't encode character '\U0001f440' in position 0: illegal multibyte sequence
```

### 解决方案

#### 方案一：强制 UTF-8 编码（推荐）

**Python 脚本开头添加：**
```python
import sys
import io

# 强制 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

**文件读写指定编码：**
```python
# 读取文件
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 写入文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
```

**环境变量设置（PowerShell）：**
```powershell
$env:PYTHONIOENCODING = "utf-8"
chcp 65001  # 切换控制台为 UTF-8
```

#### 方案二：过滤非 GBK 字符

```python
def safe_gbk(text):
    """将无法用 GBK 编码的字符替换为占位符"""
    return text.encode('gbk', errors='replace').decode('gbk')

def remove_emoji(text):
    """移除 emoji 等特殊字符"""
    import re
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)
```

#### 方案三：PowerShell 输出处理

```powershell
# 输出前设置编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
# 或
$OutputEncoding = [System.Text.Encoding]::UTF8
```

### 最佳实践

| 场景 | 推荐方案 |
|------|----------|
| Python 脚本输出 | 方案一（强制 UTF-8） |
| 读取用户文件 | 方案一（指定 encoding='utf-8'） |
| 控制台显示含 emoji | 方案二（过滤或替换） |
| PowerShell 输出 | 方案三 |
| 日志记录 | 方案一 + 方案二组合 |

---

## 二、路径处理

### 问题背景

Windows 使用反斜杠 `\` 作为路径分隔符，与 Unix 系统的正斜杠 `/` 不同，容易导致跨平台问题。

### 最佳实践

**使用 Path 对象（推荐）：**
```python
from pathlib import Path

# 跨平台路径
config_path = Path('.copaw') / 'config.json'
db_path = Path('.copaw') / '.agent-memory' / 'memory.db'

# 转换为字符串
str_path = str(config_path)
```

**使用原始字符串：**
```python
# Windows 路径使用原始字符串
path = r"D:\Users\YourName\Documents\.copaw\config.json"
```

**避免硬编码路径：**
```python
# ❌ 不好 - 硬编码路径暴露用户信息
path = "D:\\Users\\YourName\\Documents\\.copaw\\config.json"

# ✅ 好 - 使用环境变量或相对路径
import os
base_path = os.environ.get('COPAW_ROOT', '.')
config_path = os.path.join(base_path, '.copaw', 'config.json')
```

---

## 三、SSL 证书问题

### 问题背景

Windows 环境下 Python `requests` 库调用 HTTPS API 时可能出现 SSL 证书验证错误。

### 解决方案

```python
import urllib.request
import ssl

# 创建跳过 SSL 验证的上下文
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 使用 urllib 发送请求
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ssl_context) as resp:
    data = resp.read().decode()
```

**注意事项：**
- 仅用于调试或内部工具
- 生产环境应正确配置 SSL 证书

---

## 四、虚拟环境

### 创建虚拟环境

```powershell
# 使用 venv
python -m venv copaw-env

# 激活（PowerShell）
.\copaw-env\Scripts\Activate.ps1

# 激活（CMD）
.\copaw-env\Scripts\activate.bat
```

### 如果遇到执行策略错误

```powershell
# 临时允许脚本执行
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

---

## 五、GitHub API 调用

### 问题背景

Windows 环境下使用 curl 或浏览器操作 GitHub 可能遇到编码或 SSL 问题。

### 推荐方案

**使用 PowerShell 调用 GitHub API：**

```powershell
# 设置 Token
$token = "your-github-token"
$headers = @{
    "Authorization" = "token $token"
    "Accept" = "application/vnd.github.v3+json"
}

# 获取用户信息
$response = Invoke-RestMethod -Uri "https://api.github.com/user" -Headers $headers
Write-Host $response.login

# 创建 Issue
$body = @{
    title = "Issue Title"
    body = "Issue Body"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "https://api.github.com/repos/owner/repo/issues" -Method Post -Headers $headers -Body $body
```

---

## 六、HuggingFace 镜像配置

### 问题背景

国内访问 HuggingFace 较慢，需要配置镜像加速。

### 解决方案

**设置环境变量：**

```powershell
# 用户级环境变量（永久）
[Environment]::SetEnvironmentVariable("HF_ENDPOINT", "https://hf-mirror.com", "User")

# 临时环境变量（当前会话）
$env:HF_ENDPOINT = "https://hf-mirror.com"
```

**Python 代码中设置：**
```python
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
```

---

## 七、启动优化

### 问题背景

CoPaw 启动时可能需要 3-4 分钟，主要卡在模型下载和验证。

### 优化方案

**1. 使用本地模型**
```json
// .copaw.secret/providers/builtin/ollama.json
{
    "base_url": "http://127.0.0.1:11434",
    "api_key": "ollama",
    "chat_model": "qwen2.5:14b"
}
```

**2. 配置本地 Embedding**
```json
// config.json
{
    "running": {
        "embedding_config": {
            "backend": "openai",
            "api_key": "ollama",
            "base_url": "http://127.0.0.1:11434/v1",
            "model_name": "bge-m3"
        }
    }
}
```

**3. 预下载模型**
```powershell
# 使用 Ollama 预下载模型
ollama pull qwen2.5:14b
ollama pull bge-m3
```

---

## 八、常见错误排查

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `gbk codec can't encode` | 编码问题 | 强制 UTF-8 编码 |
| `SSL: CERTIFICATE_VERIFY_FAILED` | SSL 证书问题 | 跳过验证或配置证书 |
| `File not found` | 路径问题 | 使用 Path 对象 |
| `Permission denied` | 权限问题 | 检查执行策略 |
| `Connection refused` | 服务未启动 | 检查 Ollama 服务 |

---

## 相关文档

- [升级应急手册](upgrade-playbook.md)
- [GitHub 工作流规范](github-workflow.md)