# MemoryCoreClaw Best Practices: Dream Distillation Mechanism

> **Status:** Production-Ready (v3.3)
> **Author:** Mr. Lee & The MemoryCoreClaw Team
> **Last Updated:** 2026-04-18

## 📘 Overview

The **Dream Distillation (梦境蒸馏)** mechanism is an automated memory maintenance pipeline for the `MemoryCoreClaw` system. It transforms fragmented, short-term logs into structured, high-value long-term knowledge, ensuring the memory database remains lean, conflict-free, and semantically rich.

It operates as a background "janitor" that runs weekly, preventing memory bloat and automatically surfacing behavioral rules derived from past interactions.

## 🏗️ Architecture: The 5-Phase Pipeline

The distillation process is divided into five distinct phases, executed sequentially with fail-safe mechanisms at each step.

### Phase 1: Audit (Dry Run)
- **Goal:** Scan the database for potential conflicts, duplicates, and low-importance entries without making changes.
- **Mechanism:** Uses Jaccard similarity for fast keyword matching and Embedding similarity for semantic analysis.
- **Output:** Generates a health report (log only).

### Phase 2: Intelligent Cleaning
- **Goal:** Remove noise while protecting critical rules.
- **Actions:**
  - **Decay:** Applies an importance decay factor (e.g., `importance * 0.95`) to old `event/log` entries that haven't been accessed recently.
  - **Exemption:** Critical categories like `rule`, `path`, and `preference` are **immune to decay**.
  - **Threshold:** Entries with importance dropping below a floor (e.g., `0.3`) are soft-deleted.

### Phase 3: Core Extraction (LLM Powered)
- **Goal:** Distill actionable insights from raw data.
- **Mechanism:**
  - Uses an LLM (Smart Provider routing: Cloud fallback to Local Ollama) to analyze top-ranked memories.
  - Extracts high-level behavioral rules (e.g., "Always confirm before deleting files").
- **Fail-Safe:** If the LLM service times out, the script retains the previous rule set instead of crashing or generating garbage.

### Phase 4: MEMORY.md Atomic Update
- **Goal:** Synchronize the distilled content back to the human-readable `MEMORY.md` file.
- **Key Innovation: Anchor-Based Update (`<!-- START_AUTO -->`)**
  - The script identifies a specific auto-managed block within `MEMORY.md`.
  - **Deduplication:** Before writing, it checks if the new content already exists in the manual sections of the file to prevent duplication.
  - **Multi-Anchor Fuse:** If the file is corrupted (e.g., multiple anchors found), the script **aborts immediately** to prevent further damage.
  - **Atomic Write:** Uses a `.tmp` file and `os.replace` to ensure file integrity even if the process is killed.

### Phase 5: Archive & Notification
- **Goal:** Long-term storage management.
- **Actions:**
  - Moves daily notes older than 30 days to an `archive/` directory, organized by month.
  - Attempts to update `config.json` search paths (with strict validation).
  - Updates `HEARTBEAT.md` with execution summaries.

## 🛡️ Production-Grade Safeguards

### 1. Concurrency Protection (WAL Mode)
- The script enforces `PRAGMA journal_mode=WAL` and `PRAGMA busy_timeout=8000` on the SQLite database.
- Prevents "Database is locked" errors when the Agent is reading/writing memory simultaneously.

### 2. Smart Debounce (Anti-Spam)
- Integrated with the Heartbeat system.
- Uses a `.last_run_distiller` timestamp file to ensure the full pipeline runs only **once per week**, even if the heartbeat triggers multiple times.

### 3. LLM Routing & Fallback
- **Primary:** Internal Cloud API (High performance).
- **Fallback:** Local Ollama (Offline capability).
- **Network:** Proxies are disabled for internal requests to prevent timeout issues.

## ⚙️ Configuration Example

To enable Dream Distillation in your QwenPaw/CoPaw environment:

### 1. Heartbeat Configuration
Edit `HEARTBEAT.md` to include the weekly trigger:

```markdown
## Dream Distiller (Weekly Heartbeat)
- **Schedule:** 10:00 - 13:00 Window.
- **Debounce:** Check `skills/memorycoreclaw/.last_run_distiller`. If updated within 7 days, skip.
- **Command:** `python skills/memorycoreclaw/scripts/dream_distiller.py`
- **Mode:** Silent Run (Log to console only).
```

### 2. File Structure
Ensure the following structure exists:
```text
skills/memorycoreclaw/
├── scripts/
│   └── dream_distiller.py   # The main executable
├── .last_run_distiller      # Debounce state file
└── SKILL.md
```

## 🚀 Usage

Run manually for testing:
```bash
python skills/memorycoreclaw/scripts/dream_distiller.py
```

**Expected Output:**
```text
🚀 Starting Dream Distiller v3.3...
[Phase 2] Intelligent Cleaning...
   ✅ No data requires decay.
[Phase 3] Core Extraction...
   ✨ New Rule Extracted: "Verify before action."
[Phase 4] Updating MEMORY.md...
   ✅ MEMORY.md updated (Atomic Write).
[Phase 5] Archiving...
   📦 Archived 3 files to archive/2026-03/.
✅ Distillation Complete.
```

## 📝 Lessons Learned
1. **Don't Touch Configs Blindly:** Never modify `config.json` without a backup and validation. Use try-catch blocks.
2. **File Bloat Prevention:** Always implement deduplication before appending to `MEMORY.md`. We fixed a bug where anchors were duplicated 180 times!
3. **Silence is Golden:** Background tasks should not spam the user. Use silent modes and summary logs.
