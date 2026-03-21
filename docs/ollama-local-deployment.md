# Ollama 本地部署指南

> **版本：** 1.0
> **用途：** 使用 Ollama 部署本地 LLM，为 CoPaw 提供本地化 AI 能力

---

## 一、为什么使用本地 LLM

| 优势 | 说明 |
|------|------|
| **隐私保护** | 数据不出本地，适合敏感场景 |
| **成本控制** | 无 API 调用费用 |
| **稳定性** | 不受网络波动影响 |
| **可定制** | 可加载特定模型 |

---

## 二、Ollama 安装

### Windows

1. 下载：https://ollama.com/download
2. 运行安装程序
3. 验证安装：
```powershell
ollama --version
```

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### macOS

```bash
brew install ollama
```

---

## 三、模型管理

### 常用模型

| 模型 | 大小 | 用途 |
|------|------|------|
| `qwen2.5:7b` | 4.7 GB | 通用对话 |
| `qwen2.5:14b` | 9 GB | 高质量对话 |
| `bge-m3` | 1.2 GB | Embedding（向量） |
| `nomic-embed-text` | 274 MB | 轻量 Embedding |

### 模型操作

```powershell
# 下载模型
ollama pull qwen2.5:14b
ollama pull bge-m3

# 查看已安装模型
ollama list

# 删除模型
ollama rm model-name

# 运行模型（交互模式）
ollama run qwen2.5:14b
```

---

## 四、CoPaw 配置

### 1. 配置 LLM 提供商

**文件位置：** `.copaw.secret/providers/builtin/ollama.json`

```json
{
    "base_url": "http://127.0.0.1:11434",
    "api_key": "ollama",
    "chat_model": "qwen2.5:14b"
}
```

**注意：** `base_url` 必须包含 `http://` 前缀！

### 2. 配置 Embedding

**文件位置：** `.copaw/config.json`

```json
{
    "running": {
        "embedding_config": {
            "backend": "openai",
            "api_key": "ollama",
            "base_url": "http://127.0.0.1:11434/v1",
            "model_name": "bge-m3",
            "dimensions": 1024
        }
    }
}
```

### 3. 环境变量（可选）

```powershell
# 用户级环境变量
[Environment]::SetEnvironmentVariable("EMBEDDING_API_KEY", "ollama", "User")
[Environment]::SetEnvironmentVariable("EMBEDDING_BASE_URL", "http://localhost:11434", "User")
[Environment]::SetEnvironmentVariable("EMBEDDING_MODEL", "bge-m3", "User")
```

---

## 五、API 使用

### OpenAI 兼容 API

Ollama 提供 OpenAI 兼容 API，可以直接使用 OpenAI SDK：

```python
from openai import OpenAI

client = OpenAI(
    api_key="ollama",
    base_url="http://127.0.0.1:11434/v1"
)

response = client.chat.completions.create(
    model="qwen2.5:14b",
    messages=[
        {"role": "user", "content": "你好"}
    ]
)

print(response.choices[0].message.content)
```

### Embedding API

```python
from openai import OpenAI

client = OpenAI(
    api_key="ollama",
    base_url="http://127.0.0.1:11434/v1"
)

response = client.embeddings.create(
    model="bge-m3",
    input="要向量化的文本"
)

embedding = response.data[0].embedding
print(f"向量维度: {len(embedding)}")  # 1024
```

---

## 六、常见问题

### Q1: Ollama 服务未启动

**现象：** `Connection refused` 错误

**解决：**
```powershell
# 启动 Ollama 服务
ollama serve

# 或在后台运行
Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
```

### Q2: 模型下载慢

**解决：** 使用国内镜像或代理

### Q3: 内存不足

**解决：** 选择更小的模型，如 `qwen2.5:7b` 或 `qwen2.5:3b`

### Q4: GPU 未被使用

**检查：**
```powershell
nvidia-smi  # 查看 GPU 状态
```

---

## 七、性能优化

### 模型选择建议

| 场景 | 推荐模型 | 内存需求 |
|------|----------|----------|
| 轻量对话 | qwen2.5:3b | 4 GB |
| 日常对话 | qwen2.5:7b | 8 GB |
| 高质量对话 | qwen2.5:14b | 16 GB |
| Embedding | bge-m3 | 2 GB |

### 启动优化

1. **预下载模型**：启动前确保模型已下载
2. **保持服务运行**：避免每次启动都加载模型
3. **使用更小的模型**：根据需求选择

---

## 八、与其他服务对比

| 服务 | 优点 | 缺点 |
|------|------|------|
| **Ollama** | 本地部署、免费、隐私 | 需要硬件资源 |
| **OpenAI API** | 质量高、稳定 | 需付费、数据出境 |
| **Azure OpenAI** | 企业级、合规 | 需付费、配置复杂 |

---

## 相关文档

- [Windows 环境最佳实践](windows-best-practices.md)
- [MemoryCoreClaw 技能](../skills/memorycoreclaw/)