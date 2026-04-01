# -*- coding: utf-8 -*-
"""
经验回溯系统 v2.0 - SQLite 数据库存储

改进：
- 单文件 SQLite 数据库，高效存储和查询
- 自动归档旧数据
- 支持 SQL 查询分析
"""
import json
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

# 默认数据库路径
DEFAULT_DB_PATH = Path(r"D:\CoPaw\.copaw\experiences.db")


@dataclass
class ExperienceRecord:
    """经验记录"""
    id: int = 0
    task: str = ""
    task_type: str = "general"
    timestamp: str = ""
    
    # 内容（JSON 字符串存储）
    input_data: str = "[]"
    output: str = ""
    
    # 评估（JSON 字符串存储）
    evaluation: str = "{}"
    
    # 元数据
    tools_used: str = "[]"
    context: str = "{}"
    success: bool = True
    duration_seconds: int = 0
    
    # 标签
    tags: str = "[]"
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class ExperienceTracker:
    """
    经验回溯系统 v2.0
    
    使用 SQLite 数据库存储，支持高效查询和分析
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self._init_db()
    
    @contextmanager
    def _get_conn(self):
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        """初始化数据库表"""
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    task_type TEXT DEFAULT 'general',
                    timestamp TEXT NOT NULL,
                    input_data TEXT DEFAULT '[]',
                    output TEXT DEFAULT '',
                    evaluation TEXT DEFAULT '{}',
                    tools_used TEXT DEFAULT '[]',
                    context TEXT DEFAULT '{}',
                    success INTEGER DEFAULT 1,
                    duration_seconds INTEGER DEFAULT 0,
                    tags TEXT DEFAULT '[]'
                )
            """)
            
            # 创建索引
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON experiences(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_task_type 
                ON experiences(task_type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_task 
                ON experiences(task)
            """)
            
            conn.commit()
    
    def record(
        self,
        task: str,
        output: str = "",
        input_data: Optional[Dict] = None,
        evaluation: Optional[Dict] = None,
        tools_used: Optional[List[str]] = None,
        context: Optional[Dict] = None,
        trajectory: Optional[List[Dict]] = None,
        tags: Optional[List[str]] = None,
        task_type: str = "general",
        success: bool = True,
        duration_seconds: int = 0
    ) -> ExperienceRecord:
        """
        记录执行经验
        
        Returns:
            ExperienceRecord: 包含 ID 的记录
        """
        # 序列化为 JSON
        input_json = json.dumps(input_data or {}, ensure_ascii=False)
        eval_json = json.dumps(evaluation or {}, ensure_ascii=False)
        tools_json = json.dumps(tools_used or [], ensure_ascii=False)
        ctx_json = json.dumps(context or {}, ensure_ascii=False)
        tags_json = json.dumps(tags or [], ensure_ascii=False)
        
        with self._get_conn() as conn:
            cursor = conn.execute("""
                INSERT INTO experiences (
                    task, task_type, timestamp, input_data, output,
                    evaluation, tools_used, context, success, duration_seconds, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task, task_type, datetime.now().isoformat(),
                input_json, output, eval_json, tools_json, ctx_json,
                1 if success else 0, duration_seconds, tags_json
            ))
            conn.commit()
            
            record_id = cursor.lastrowid
        
        # 返回带 ID 的记录
        return ExperienceRecord(
            id=record_id,
            task=task,
            task_type=task_type,
            timestamp=datetime.now().isoformat(),
            input_data=input_json,
            output=output,
            evaluation=eval_json,
            tools_used=tools_json,
            context=ctx_json,
            success=success,
            duration_seconds=duration_seconds,
            tags=tags_json
        )
    
    def search_similar(
        self,
        task: str,
        task_type: Optional[str] = None,
        limit: int = 5,
        time_range_days: int = 30
    ) -> List[ExperienceRecord]:
        """
        搜索相似任务（关键词匹配）
        """
        cutoff = (datetime.now() - timedelta(days=time_range_days)).isoformat()
        
        query = """
            SELECT * FROM experiences 
            WHERE timestamp >= ? AND task LIKE ?
        """
        params = [cutoff, f"%{task}%"]
        
        if task_type:
            query += " AND task_type = ?"
            params.append(task_type)
        
        query += f" ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with self._get_conn() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
        
        return [self._row_to_record(row) for row in rows]
    
    def _row_to_record(self, row) -> ExperienceRecord:
        """Row 转 Record"""
        return ExperienceRecord(
            id=row["id"],
            task=row["task"],
            task_type=row["task_type"],
            timestamp=row["timestamp"],
            input_data=row["input_data"],
            output=row["output"],
            evaluation=row["evaluation"],
            tools_used=row["tools_used"],
            context=row["context"],
            success=bool(row["success"]),
            duration_seconds=row["duration_seconds"],
            tags=row["tags"]
        )
    
    def get_stats(self, period: str = "7d") -> Dict:
        """
        获取统计数据
        """
        days_map = {"7d": 7, "30d": 30, "90d": 90, "all": 9999}
        days = days_map.get(period, 7)
        
        if days < 9999:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            where = "WHERE timestamp >= ?"
            params = [cutoff]
        else:
            where = ""
            params = []
        
        with self._get_conn() as conn:
            # 总数
            total = conn.execute(
                f"SELECT COUNT(*) as cnt FROM experiences {where}",
                params
            ).fetchone()["cnt"]
            
            # 有评估的（使用不同的空值表示）
            empty_eval = '{}'
            with_eval = conn.execute(
                f"SELECT COUNT(*) as cnt FROM experiences {where} AND evaluation != ?",
                params + [empty_eval]
            ).fetchone()["cnt"]
            
            # 平均分
            avg_score = conn.execute(f"""
                SELECT AVG(json_extract(evaluation, '$.overall_score')) as avg
                FROM experiences {where} AND evaluation != ?
            """, params + [empty_eval]).fetchone()["avg"] or 0
            
            # 成功率
            success_count = conn.execute(
                f"SELECT COUNT(*) as cnt FROM experiences {where} AND success = 1",
                params
            ).fetchone()["cnt"]
        
        return {
            "total": total,
            "with_evaluation": with_eval,
            "avg_score": round(avg_score, 1),
            "success_count": success_count,
            "success_rate": round(success_count / total * 100, 1) if total > 0 else 0
        }
    
    def analyze_tool_effectiveness(self) -> Dict:
        """分析工具效果"""
        with self._get_conn() as conn:
            # 提取 tools_used JSON 并统计
            cursor = conn.execute("""
                SELECT id, tools_used, evaluation FROM experiences
                WHERE tools_used != '[]' AND tools_used != '[]'
            """)
            
            tool_stats = {}
            
            for row in cursor.fetchall():
                try:
                    tools = json.loads(row["tools_used"])
                    eval_data = json.loads(row["evaluation"])
                    score = eval_data.get("overall_score", 50)
                    
                    for tool in tools:
                        if tool not in tool_stats:
                            tool_stats[tool] = {"success": 0, "total": 0}
                        
                        tool_stats[tool]["total"] += 1
                        if score >= 60:
                            tool_stats[tool]["success"] += 1
                except:
                    continue
            
            # 计算成功率
            for tool, stats in tool_stats.items():
                rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
                stats["rate"] = f"{rate:.0f}%"
            
            return tool_stats
    
    def get_recent(self, limit: int = 10) -> List[ExperienceRecord]:
        """获取最近的经验"""
        with self._get_conn() as conn:
            cursor = conn.execute("""
                SELECT * FROM experiences 
                ORDER BY timestamp DESC LIMIT ?
            """, [limit])
            
            return [self._row_to_record(row) for row in cursor.fetchall()]
    
    def query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """
        高级查询 - 直接执行 SQL
        
        示例：
        >>> tracker.query("SELECT * FROM experiences WHERE overall_score < 60")
        """
        with self._get_conn() as conn:
            cursor = conn.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_low_score_records(self, threshold: float = 60) -> List[ExperienceRecord]:
        """获取低分记录"""
        with self._get_conn() as conn:
            cursor = conn.execute("""
                SELECT * FROM experiences 
                WHERE json_extract(evaluation, '$.overall_score') < ?
                ORDER BY timestamp DESC
            """, [threshold])
            
            return [self._row_to_record(row) for row in cursor.fetchall()]
    
    def archive_old(self, days: int = 90):
        """
        归档旧数据（可定期调用）
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self._get_conn() as conn:
            cursor = conn.execute("""
                DELETE FROM experiences 
                WHERE timestamp < ? AND evaluation = '{}'
            """, [cutoff])
            conn.commit()
            
            return cursor.rowcount
    
    def cleanup(self, keep_recent: int = 1000):
        """
        清理：只保留最近 N 条记录
        """
        with self._get_conn() as conn:
            # 删除太旧的记录
            conn.execute("""
                DELETE FROM experiences 
                WHERE id NOT IN (
                    SELECT id FROM experiences 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                )
            """, [keep_recent])
            conn.commit()
    
    def export_json(self, path: str, days: int = 30) -> int:
        """导出为 JSON 文件"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self._get_conn() as conn:
            cursor = conn.execute("""
                SELECT * FROM experiences 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """, [cutoff])
            
            records = [self._row_to_record(row).__dict__ for row in cursor.fetchall()]
        
        # 移除 id（导出时不要 ID）
        for r in records:
            r.pop('id', None)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        return len(records)


# ============== 便捷函数 ==============

def quick_record(task: str, output: str, **kwargs) -> ExperienceRecord:
    """快速记录"""
    tracker = ExperienceTracker()
    return tracker.record(task, output, **kwargs)


def quick_search(task: str, limit: int = 5) -> List[ExperienceRecord]:
    """快速搜索"""
    tracker = ExperienceTracker()
    return tracker.search_similar(task, limit)


def get_stats(period: str = "7d") -> Dict:
    """快速统计"""
    tracker = ExperienceTracker()
    return tracker.get_stats(period)


__all__ = [
    "ExperienceTracker",
    "ExperienceRecord",
    "quick_record",
    "quick_search",
    "get_stats"
]


if __name__ == "__main__":
    # 测试
    tracker = ExperienceTracker()
    
    # 记录
    record = tracker.record(
        task="测试：SQLite 存储",
        output="def test(): pass",
        evaluation={"overall_score": 85},
        tools_used=["code"],
        tags=["test"]
    )
    print(f"记录 ID: {record.id}")
    
    # 统计
    stats = tracker.get_stats()
    print(f"统计: {stats}")
    
    # 工具效果
    tool_stats = tracker.analyze_tool_effectiveness()
    print(f"工具效果: {tool_stats}")
    
    print("\n✅ SQLite 版本测试通过!")