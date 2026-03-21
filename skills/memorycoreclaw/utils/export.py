"""
MemoryCoreClaw - Memory Export Module

Export memory to various formats.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class MemoryExporter:
    """
    Memory Exporter
    
    Export memories to JSON, Markdown, or other formats.
    """
    
    def __init__(self, memory_engine):
        self.engine = memory_engine
    
    def export_json(self, output_path: str = None) -> Dict:
        """
        Export all memory to JSON.
        
        Args:
            output_path: Optional file path to save
            
        Returns:
            Export data dict
        """
        data = self.engine.export_json()
        
        if output_path:
            Path(output_path).write_text(
                json.dumps(data, indent=2, ensure_ascii=False, default=str),
                encoding='utf-8'
            )
        
        return data
    
    def export_markdown(self, output_path: str = None) -> str:
        """
        Export memory to Markdown format.
        
        Args:
            output_path: Optional file path to save
            
        Returns:
            Markdown string
        """
        stats = self.engine.get_stats()
        lessons = self.engine.get_lessons()
        
        lines = [
            "# Memory Export",
            f"\nExported: {datetime.now().isoformat()}",
            f"\n## Statistics",
            f"- Facts: {stats['facts']}",
            f"- Lessons: {stats['experiences']}",
            f"- Relations: {stats['relations']}",
        ]
        
        if lessons:
            lines.append("\n## Learned Lessons\n")
            for i, lesson in enumerate(lessons, 1):
                lines.append(f"### Lesson {i}")
                lines.append(f"- **Action:** {lesson['action']}")
                lines.append(f"- **Context:** {lesson['context']}")
                lines.append(f"- **Outcome:** {lesson['outcome']}")
                lines.append(f"- **Insight:** {lesson['insight']}")
                lines.append("")
        
        md_content = "\n".join(lines)
        
        if output_path:
            Path(output_path).write_text(md_content, encoding='utf-8')
        
        return md_content
    
    def import_json(self, data: Dict):
        """
        Import memory from JSON.
        
        Args:
            data: Import data dict
        """
        # Import facts
        for fact in data.get('facts', []):
            self.engine.remember(
                content=fact.get('content', ''),
                importance=fact.get('importance', 0.5),
                category=fact.get('category', 'general'),
                emotion=fact.get('emotion', 'neutral')
            )
        
        # Import experiences
        for exp in data.get('experiences', []):
            self.engine.learn(
                action=exp.get('action', ''),
                context=exp.get('context', ''),
                outcome=exp.get('outcome', 'neutral'),
                insight=exp.get('insight', ''),
                importance=exp.get('importance', 0.5)
            )
        
        # Import relations
        for rel in data.get('relations', []):
            self.engine.relate(
                from_entity=rel.get('from_entity', ''),
                relation_type=rel.get('relation_type', 'related_to'),
                to_entity=rel.get('to_entity', '')
            )