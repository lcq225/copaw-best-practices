"""
MemoryCoreClaw - Memory Visualization Module

Generate knowledge graphs and visualizations.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json
import sqlite3


class MemoryVisualizer:
    """
    Memory Visualizer
    
    Generate HTML knowledge graphs and statistics reports.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize visualizer with database path.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
    
    def _get_all_relations(self) -> List[Dict]:
        """Get all relations from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT from_entity, relation_type, to_entity, weight, evidence
            FROM relations
        ''')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'from_entity': row[0],
                'relation_type': row[1],
                'to_entity': row[2],
                'weight': row[3] or 1.0,
                'evidence': row[4] or ''
            })
        
        conn.close()
        return results
    
    def _get_all_entities(self) -> List[Dict]:
        """Get all entities from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, type, metadata
            FROM entities
        ''')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'name': row[0],
                'entity_type': row[1] or 'unknown',
                'metadata': row[2]
            })
        
        conn.close()
        return results
    
    def _get_all_facts(self) -> List[Dict]:
        """Get all facts from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, content, importance, category, emotion
            FROM facts
            ORDER BY importance DESC
        ''')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'content': row[1],
                'importance': row[2],
                'category': row[3],
                'emotion': row[4]
            })
        
        conn.close()
        return results
    
    def _get_all_lessons(self) -> List[Dict]:
        """Get all lessons from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, action, context, outcome, insight, importance
            FROM experiences
            ORDER BY importance DESC
        ''')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'action': row[1],
                'context': row[2],
                'outcome': row[3],
                'insight': row[4],
                'importance': row[5]
            })
        
        conn.close()
        return results
    
    def generate_knowledge_graph(self, output_path: str = None) -> str:
        """
        Generate an interactive knowledge graph HTML.
        
        Args:
            output_path: Optional file path to save
            
        Returns:
            HTML content
        """
        # Get real data from database
        relations = self._get_all_relations()
        entities = self._get_all_entities()
        
        # Build nodes from entities and relations
        node_set = set()
        for rel in relations:
            node_set.add(rel['from_entity'])
            node_set.add(rel['to_entity'])
        
        # Also include entities from entities table
        for ent in entities:
            node_set.add(ent['name'])
        
        # Create nodes with types
        entity_types = {e['name']: e['entity_type'] for e in entities}
        
        nodes = []
        for name in sorted(node_set):
            nodes.append({
                'id': name,
                'type': entity_types.get(name, 'unknown'),
                'size': 20  # Base size
            })
        
        # Create edges
        edges = []
        for rel in relations:
            edges.append({
                'source': rel['from_entity'],
                'target': rel['to_entity'],
                'type': rel['relation_type'],
                'weight': rel['weight']
            })
        
        # Generate HTML
        html = self._generate_html(nodes, edges)
        
        if output_path:
            Path(output_path).write_text(html, encoding='utf-8')
        
        return html
    
    def _generate_html(self, nodes: List[Dict], edges: List[Dict]) -> str:
        """Generate D3.js force-directed graph HTML"""
        
        nodes_json = json.dumps(nodes, ensure_ascii=False)
        edges_json = json.dumps(edges, ensure_ascii=False)
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>MemoryCoreClaw - Knowledge Graph</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }}
        .header {{
            padding: 20px;
            text-align: center;
            background: rgba(0,0,0,0.2);
        }}
        .header h1 {{
            font-size: 24px;
            margin-bottom: 5px;
        }}
        .header p {{
            color: #888;
            font-size: 14px;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            padding: 10px;
            background: rgba(0,0,0,0.1);
        }}
        .stat {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 28px;
            font-weight: bold;
            color: #4ecca3;
        }}
        .stat-label {{
            font-size: 12px;
            color: #888;
        }}
        .container {{
            display: flex;
            height: calc(100vh - 150px);
        }}
        #graph {{
            flex: 1;
            border-right: 1px solid rgba(255,255,255,0.1);
        }}
        #sidebar {{
            width: 350px;
            padding: 20px;
            overflow-y: auto;
            background: rgba(0,0,0,0.2);
        }}
        .sidebar-title {{
            font-size: 16px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .node-info {{
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
        }}
        .node-name {{
            font-size: 18px;
            font-weight: bold;
            color: #4ecca3;
            margin-bottom: 10px;
        }}
        .node-type {{
            display: inline-block;
            padding: 2px 8px;
            background: rgba(78, 204, 163, 0.2);
            border-radius: 4px;
            font-size: 12px;
            margin-bottom: 10px;
        }}
        .relations-list {{
            margin-top: 10px;
        }}
        .relation-item {{
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 13px;
        }}
        .relation-arrow {{
            color: #ff6b6b;
            margin: 0 5px;
        }}
        .legend {{
            margin-top: 20px;
            padding: 15px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
        }}
        .legend-title {{
            font-size: 14px;
            margin-bottom: 10px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
            font-size: 12px;
        }}
        .legend-color {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .instructions {{
            margin-top: 20px;
            padding: 15px;
            background: rgba(78, 204, 163, 0.1);
            border-radius: 8px;
            font-size: 12px;
            line-height: 1.6;
        }}
        .instructions h4 {{
            margin-bottom: 8px;
            color: #4ecca3;
        }}
        svg {{
            width: 100%;
            height: 100%;
        }}
        .node {{
            cursor: pointer;
        }}
        .node circle {{
            stroke-width: 2px;
        }}
        .node text {{
            font-size: 12px;
            fill: #fff;
            pointer-events: none;
        }}
        .link {{
            stroke-opacity: 0.6;
        }}
        .link text {{
            font-size: 10px;
            fill: #888;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>MemoryCoreClaw Knowledge Graph</h1>
        <p>Interactive Entity Relationship Visualization</p>
    </div>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-value">{len(nodes)}</div>
            <div class="stat-label">Entities</div>
        </div>
        <div class="stat">
            <div class="stat-value">{len(edges)}</div>
            <div class="stat-label">Relations</div>
        </div>
    </div>
    
    <div class="container">
        <div id="graph"></div>
        <div id="sidebar">
            <div class="sidebar-title">Node Details</div>
            <div id="node-details">
                <p style="color: #888;">Click a node to see details</p>
            </div>
            
            <div class="legend">
                <div class="legend-title">Relation Types</div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #4ecca3;"></div>
                    <span>works_at / located_in</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #ff6b6b;"></div>
                    <span>prefers / likes</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #ffd93d;"></div>
                    <span>uses / depends_on</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #6bcb77;"></div>
                    <span>knows / collaborates_with</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #4d96ff;"></div>
                    <span>other relations</span>
                </div>
            </div>
            
            <div class="instructions">
                <h4>Instructions</h4>
                <ul>
                    <li>Drag nodes to reposition</li>
                    <li>Click node to see details</li>
                    <li>Scroll to zoom</li>
                    <li>Drag background to pan</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script>
        const nodes = {nodes_json};
        const links = {edges_json};
        
        // Create relation type colors
        const relationColors = {{
            'works_at': '#4ecca3',
            'works_in': '#4ecca3',
            'located_in': '#4ecca3',
            'part_of': '#4ecca3',
            'prefers': '#ff6b6b',
            'likes': '#ff6b6b',
            'dislikes': '#ff6b6b',
            'uses': '#ffd93d',
            'depends_on': '#ffd93d',
            'implements': '#ffd93d',
            'knows': '#6bcb77',
            'collaborates_with': '#6bcb77',
            'reports_to': '#6bcb77',
            'manages': '#6bcb77'
        }};
        
        function getRelationColor(type) {{
            return relationColors[type] || '#4d96ff';
        }}
        
        // Setup SVG
        const container = document.getElementById('graph');
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        const svg = d3.select('#graph')
            .append('svg')
            .attr('viewBox', [0, 0, width, height]);
        
        // Add zoom behavior
        const g = svg.append('g');
        
        svg.call(d3.zoom()
            .extent([[0, 0], [width, height]])
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {{
                g.attr('transform', event.transform);
            }}));
        
        // Create force simulation
        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(150))
            .force('charge', d3.forceManyBody().strength(-500))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(40));
        
        // Draw links
        const link = g.append('g')
            .selectAll('line')
            .data(links)
            .enter()
            .append('line')
            .attr('class', 'link')
            .attr('stroke', d => getRelationColor(d.type))
            .attr('stroke-width', 2);
        
        // Draw link labels
        const linkLabel = g.append('g')
            .selectAll('text')
            .data(links)
            .enter()
            .append('text')
            .attr('font-size', 10)
            .attr('fill', '#888')
            .attr('dy', -5)
            .text(d => d.type);
        
        // Draw nodes
        const node = g.append('g')
            .selectAll('g')
            .data(nodes)
            .enter()
            .append('g')
            .attr('class', 'node')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
        
        node.append('circle')
            .attr('r', 20)
            .attr('fill', '#2d3436')
            .attr('stroke', '#4ecca3')
            .attr('stroke-width', 2);
        
        node.append('text')
            .attr('dy', 4)
            .attr('text-anchor', 'middle')
            .text(d => d.id.length > 8 ? d.id.substring(0, 8) + '...' : d.id);
        
        // Node click handler
        node.on('click', function(event, d) {{
            event.stopPropagation();
            showNodeDetails(d);
        }});
        
        // Update positions on tick
        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            linkLabel
                .attr('x', d => (d.source.x + d.target.x) / 2)
                .attr('y', d => (d.source.y + d.target.y) / 2);
            
            node.attr('transform', d => `translate(${{d.x}},${{d.y}})`);
        }});
        
        // Drag functions
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        // Show node details
        function showNodeDetails(nodeData) {{
            const detailsDiv = document.getElementById('node-details');
            
            // Find all relations for this node
            const relatedLinks = links.filter(l => 
                l.source.id === nodeData.id || l.target.id === nodeData.id
            );
            
            let relationsHtml = '';
            relatedLinks.forEach(link => {{
                const isSource = link.source.id === nodeData.id;
                const other = isSource ? link.target.id : link.source.id;
                const arrow = isSource ? '→' : '←';
                const relation = isSource ? link.type : `${{link.type}} (incoming)`;
                
                relationsHtml += `
                    <div class="relation-item">
                        <span>${{nodeData.id}}</span>
                        <span class="relation-arrow">${{arrow}}</span>
                        <span style="color: ${{getRelationColor(link.type)}}">${{relation}}</span>
                        <span class="relation-arrow">${{arrow}}</span>
                        <span>${{other}}</span>
                    </div>
                `;
            }});
            
            detailsDiv.innerHTML = `
                <div class="node-info">
                    <div class="node-name">${{nodeData.id}}</div>
                    <div class="node-type">${{nodeData.type}}</div>
                </div>
                <div class="relations-list">
                    <div style="font-size: 14px; margin-bottom: 10px; color: #4ecca3;">
                        Relations (${{relatedLinks.length}})
                    </div>
                    ${{relationsHtml || '<p style="color: #888;">No relations found</p>'}}
                </div>
            `;
        }}
    </script>
</body>
</html>'''
        
        return html
    
    def generate_stats_report(self, output_path: str = None) -> str:
        """
        Generate a statistics report HTML.
        
        Args:
            output_path: Optional file path to save
            
        Returns:
            HTML content
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get stats
        cursor.execute('SELECT COUNT(*) FROM facts')
        facts_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM experiences')
        lessons_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM relations')
        relations_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM entities')
        entities_count = cursor.fetchone()[0]
        
        # Get categories
        cursor.execute('SELECT category, COUNT(*) as cnt FROM facts GROUP BY category ORDER BY cnt DESC')
        categories = cursor.fetchall()
        
        # Get top entities by relation count
        cursor.execute('''
            SELECT entity, COUNT(*) as cnt FROM (
                SELECT from_entity as entity FROM relations
                UNION ALL
                SELECT to_entity as entity FROM relations
            ) GROUP BY entity ORDER BY cnt DESC LIMIT 10
        ''')
        top_entities = cursor.fetchall()
        
        # Get relation types
        cursor.execute('SELECT relation_type, COUNT(*) as cnt FROM relations GROUP BY relation_type ORDER BY cnt DESC')
        relation_types = cursor.fetchall()
        
        conn.close()
        
        # Generate HTML
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>MemoryCoreClaw - Statistics Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 40px;
        }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .header p {{ color: #888; }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .stat-value {{ font-size: 48px; font-weight: bold; color: #4ecca3; }}
        .stat-label {{ font-size: 14px; color: #888; margin-top: 10px; }}
        
        .section {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .section-title {{
            font-size: 18px;
            margin-bottom: 15px;
            color: #4ecca3;
        }}
        .list-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        .list-item:last-child {{ border-bottom: none; }}
        .count {{
            background: #4ecca3;
            color: #1a1a2e;
            padding: 2px 10px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: bold;
        }}
        .two-col {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>MemoryCoreClaw Statistics</h1>
        <p>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{facts_count}</div>
            <div class="stat-label">Facts</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{lessons_count}</div>
            <div class="stat-label">Lessons</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{relations_count}</div>
            <div class="stat-label">Relations</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{entities_count}</div>
            <div class="stat-label">Entities</div>
        </div>
    </div>
    
    <div class="two-col">
        <div class="section">
            <div class="section-title">Top Entities by Relations</div>
            {''.join(f'<div class="list-item"><span>{e[0]}</span><span class="count">{e[1]}</span></div>' for e in top_entities)}
        </div>
        
        <div class="section">
            <div class="section-title">Fact Categories</div>
            {''.join(f'<div class="list-item"><span>{c[0]}</span><span class="count">{c[1]}</span></div>' for c in categories)}
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">Relation Types</div>
        <div class="two-col">
            {''.join(f'<div class="list-item"><span>{r[0]}</span><span class="count">{r[1]}</span></div>' for r in relation_types)}
        </div>
    </div>
</body>
</html>'''
        
        if output_path:
            Path(output_path).write_text(html, encoding='utf-8')
        
        return html
    
    def generate_memory_browser(self, output_path: str = None) -> str:
        """
        Generate an interactive memory browser HTML.
        
        Args:
            output_path: Optional file path to save
            
        Returns:
            HTML content
        """
        facts = self._get_all_facts()
        lessons = self._get_all_lessons()
        relations = self._get_all_relations()
        
        facts_json = json.dumps(facts, ensure_ascii=False)
        lessons_json = json.dumps(lessons, ensure_ascii=False)
        relations_json = json.dumps(relations, ensure_ascii=False)
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>MemoryCoreClaw - Memory Browser</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }}
        .header {{
            padding: 20px;
            background: rgba(0,0,0,0.2);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .header h1 {{ font-size: 24px; margin-bottom: 10px; }}
        
        .tabs {{
            display: flex;
            gap: 10px;
        }}
        .tab {{
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            border: none;
            border-radius: 8px;
            color: #888;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }}
        .tab.active {{
            background: #4ecca3;
            color: #1a1a2e;
        }}
        .tab:hover:not(.active) {{
            background: rgba(255,255,255,0.2);
        }}
        
        .search-box {{
            margin: 20px;
        }}
        .search-box input {{
            width: 100%;
            padding: 15px 20px;
            border: none;
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            color: #fff;
            font-size: 16px;
        }}
        .search-box input::placeholder {{ color: #666; }}
        
        .content {{
            padding: 0 20px 20px;
        }}
        .panel {{ display: none; }}
        .panel.active {{ display: block; }}
        
        .card {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .card-category {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            background: rgba(78, 204, 163, 0.2);
            color: #4ecca3;
        }}
        .card-importance {{
            font-size: 12px;
            color: #888;
        }}
        .card-content {{ font-size: 14px; line-height: 1.6; }}
        
        .lesson-card .outcome {{
            margin-top: 10px;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
        }}
        .outcome.positive {{ background: rgba(107, 203, 119, 0.2); color: #6bcb77; }}
        .outcome.negative {{ background: rgba(255, 107, 107, 0.2); color: #ff6b6b; }}
        .outcome.neutral {{ background: rgba(255, 255, 255, 0.1); color: #888; }}
        
        .relation-card {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .relation-entity {{
            padding: 8px 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
        }}
        .relation-type {{
            color: #4ecca3;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>MemoryCoreClaw Browser</h1>
        <div class="tabs">
            <button class="tab active" onclick="showPanel('facts')">Facts ({len(facts)})</button>
            <button class="tab" onclick="showPanel('lessons')">Lessons ({len(lessons)})</button>
            <button class="tab" onclick="showPanel('relations')">Relations ({len(relations)})</button>
        </div>
    </div>
    
    <div class="search-box">
        <input type="text" id="search" placeholder="Search memories..." onkeyup="filter()">
    </div>
    
    <div class="content">
        <div id="facts" class="panel active"></div>
        <div id="lessons" class="panel"></div>
        <div id="relations" class="panel"></div>
    </div>
    
    <script>
        const facts = {facts_json};
        const lessons = {lessons_json};
        const relations = {relations_json};
        
        function showPanel(name) {{
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById(name).classList.add('active');
            event.target.classList.add('active');
        }}
        
        function renderFacts(data) {{
            const container = document.getElementById('facts');
            container.innerHTML = data.map(f => `
                <div class="card" data-content="${{f.content.toLowerCase()}}">
                    <div class="card-header">
                        <span class="card-category">${{f.category}}</span>
                        <span class="card-importance">Importance: ${{(f.importance * 100).toFixed(0)}}%</span>
                    </div>
                    <div class="card-content">${{f.content}}</div>
                </div>
            `).join('');
        }}
        
        function renderLessons(data) {{
            const container = document.getElementById('lessons');
            container.innerHTML = data.map(l => `
                <div class="card lesson-card" data-content="${{(l.action + l.insight).toLowerCase()}}">
                    <div class="card-header">
                        <span class="card-importance">Importance: ${{(l.importance * 100).toFixed(0)}}%</span>
                    </div>
                    <div class="card-content">
                        <strong>Action:</strong> ${{l.action}}<br>
                        <strong>Context:</strong> ${{l.context}}<br>
                        <strong>Insight:</strong> ${{l.insight}}
                    </div>
                    <div class="outcome ${{l.outcome}}">${{l.outcome.toUpperCase()}}</div>
                </div>
            `).join('');
        }}
        
        function renderRelations(data) {{
            const container = document.getElementById('relations');
            container.innerHTML = data.map(r => `
                <div class="card relation-card" data-content="${{(r.from_entity + r.to_entity + r.relation_type).toLowerCase()}}">
                    <div class="relation-entity">${{r.from_entity}}</div>
                    <div class="relation-type">${{r.relation_type}}</div>
                    <div class="relation-entity">${{r.to_entity}}</div>
                </div>
            `).join('');
        }}
        
        function filter() {{
            const query = document.getElementById('search').value.toLowerCase();
            
            document.querySelectorAll('.card').forEach(card => {{
                const content = card.dataset.content;
                card.style.display = content.includes(query) ? 'block' : 'none';
            }});
        }}
        
        // Initial render
        renderFacts(facts);
        renderLessons(lessons);
        renderRelations(relations);
    </script>
</body>
</html>'''
        
        if output_path:
            Path(output_path).write_text(html, encoding='utf-8')
        
        return html


# CLI interface
if __name__ == '__main__':
    import sys
    import os
    
    # Database path from environment variable or default
    db_path = os.environ.get('MEMORY_DB_PATH', 'memory.db')
    
    visualizer = MemoryVisualizer(db_path)
    
    # Output directory from environment variable or default
    output_dir = Path(os.environ.get('MEMORY_OUTPUT_DIR', './visualization_output'))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("MemoryCoreClaw Visualization Generator")
    print("=" * 60)
    
    # Generate knowledge graph
    kg_path = output_dir / "knowledge_graph.html"
    print(f"\n[1/3] Generating Knowledge Graph...")
    visualizer.generate_knowledge_graph(str(kg_path))
    print(f"      Saved: {kg_path}")
    
    # Generate stats report
    stats_path = output_dir / "stats_report.html"
    print(f"\n[2/3] Generating Statistics Report...")
    visualizer.generate_stats_report(str(stats_path))
    print(f"      Saved: {stats_path}")
    
    # Generate memory browser
    browser_path = output_dir / "memory_browser.html"
    print(f"\n[3/3] Generating Memory Browser...")
    visualizer.generate_memory_browser(str(browser_path))
    print(f"      Saved: {browser_path}")
    
    print("\n" + "=" * 60)
    print("All visualizations generated successfully!")
    print(f"Open in browser: file:///{str(kg_path).replace(chr(92), '/')}")
    print("=" * 60)