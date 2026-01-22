"""Message map generator for organizing customer language insights."""

import json
from typing import Dict, Any, List
from datetime import datetime
import os


class MessageMapGenerator:
    """Generates message maps with customer quotes organized by awareness stage and ad frameworks."""

    def __init__(self, output_dir: str = "./output"):
        """
        Initialize message map generator.

        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_message_map(
        self,
        analysis: Dict[str, Any],
        ad_framework: Dict[str, Any],
        raw_data: List[Dict] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive message map.

        Args:
            analysis: Customer language analysis from Claude
            ad_framework: Ad copy frameworks from Claude
            raw_data: Optional raw scraped data
            metadata: Optional metadata about the research

        Returns:
            Complete message map dictionary
        """
        message_map = {
            "generated_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "executive_summary": self._generate_summary(analysis),
            "emotional_intelligence": analysis.get("emotional_patterns", []),
            "pain_points": analysis.get("pain_points", []),
            "desire_triggers": analysis.get("desire_triggers", []),
            "awareness_stages": analysis.get("awareness_stages", {}),
            "language_patterns": analysis.get("language_patterns", {}),
            "ad_ready_hooks": ad_framework.get("hooks", {}),
            "body_copy_frameworks": ad_framework.get("body_copy_frameworks", []),
            "headline_formulas": ad_framework.get("headline_formulas", []),
            "call_to_actions": ad_framework.get("call_to_action_suggestions", []),
            "objection_handlers": ad_framework.get("objection_handlers", []),
            "key_insights": analysis.get("key_insights", []),
            "raw_data_summary": self._summarize_raw_data(raw_data) if raw_data else None
        }

        return message_map

    def _generate_summary(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate executive summary from analysis."""
        pain_points = analysis.get("pain_points", [])
        emotions = analysis.get("emotional_patterns", [])
        desires = analysis.get("desire_triggers", [])

        return {
            "top_pain_point": pain_points[0]["pain_point"] if pain_points else "N/A",
            "dominant_emotion": emotions[0]["emotion"] if emotions else "N/A",
            "primary_desire": desires[0]["desire"] if desires else "N/A",
            "total_emotional_patterns": len(emotions),
            "total_pain_points": len(pain_points),
            "total_desire_triggers": len(desires)
        }

    def _summarize_raw_data(self, raw_data: List[Dict]) -> Dict[str, Any]:
        """Summarize raw scraped data."""
        sources = {}
        total_items = len(raw_data)

        for item in raw_data:
            source = item.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1

        return {
            "total_items": total_items,
            "sources": sources,
            "date_range": self._get_date_range(raw_data)
        }

    def _get_date_range(self, raw_data: List[Dict]) -> Dict[str, str]:
        """Get date range from raw data."""
        dates = []

        for item in raw_data:
            date_str = item.get('created_utc') or item.get('published_at') or item.get('date')
            if date_str:
                dates.append(date_str)

        if dates:
            return {
                "earliest": min(dates),
                "latest": max(dates)
            }

        return {"earliest": "N/A", "latest": "N/A"}

    def save_as_json(
        self,
        message_map: Dict[str, Any],
        filename: str = None
    ) -> str:
        """
        Save message map as JSON file.

        Args:
            message_map: Message map to save
            filename: Optional custom filename

        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"message_map_{timestamp}.json"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(message_map, f, indent=2, ensure_ascii=False)

        print(f"Message map saved to: {filepath}")
        return filepath

    def save_as_markdown(
        self,
        message_map: Dict[str, Any],
        filename: str = None
    ) -> str:
        """
        Save message map as Markdown file.

        Args:
            message_map: Message map to save
            filename: Optional custom filename

        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"message_map_{timestamp}.md"

        filepath = os.path.join(self.output_dir, filename)

        markdown = self._generate_markdown(message_map)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"Message map saved to: {filepath}")
        return filepath

    def _generate_markdown(self, message_map: Dict[str, Any]) -> str:
        """Generate Markdown formatted message map."""
        md = []

        # Header
        md.append("# Customer Language Message Map")
        md.append(f"\nGenerated: {message_map.get('generated_at', 'N/A')}\n")

        # Executive Summary
        md.append("## Executive Summary\n")
        summary = message_map.get('executive_summary', {})
        md.append(f"- **Top Pain Point:** {summary.get('top_pain_point', 'N/A')}")
        md.append(f"- **Dominant Emotion:** {summary.get('dominant_emotion', 'N/A')}")
        md.append(f"- **Primary Desire:** {summary.get('primary_desire', 'N/A')}")
        md.append(f"- **Total Patterns Identified:** {summary.get('total_emotional_patterns', 0)}")
        md.append("")

        # Key Insights
        md.append("## Key Insights\n")
        for insight in message_map.get('key_insights', []):
            md.append(f"- {insight}")
        md.append("")

        # Pain Points
        md.append("## Pain Points\n")
        for i, pain in enumerate(message_map.get('pain_points', []), 1):
            md.append(f"### {i}. {pain.get('pain_point', 'N/A')}")
            md.append(f"**Severity:** {pain.get('severity', 'N/A')}")
            md.append(f"\n**Customer Quotes:**")
            for quote in pain.get('customer_quotes', []):
                md.append(f"> {quote}")
            md.append("")

        # Emotional Patterns
        md.append("## Emotional Patterns\n")
        for emotion in message_map.get('emotional_intelligence', []):
            md.append(f"### {emotion.get('emotion', 'N/A').title()}")
            md.append(f"**Frequency:** {emotion.get('frequency', 'N/A')}")
            md.append(f"**Advertising Angle:** {emotion.get('advertising_angle', 'N/A')}")
            md.append(f"\n**Example Quotes:**")
            for quote in emotion.get('example_quotes', []):
                md.append(f"> {quote}")
            md.append("")

        # Awareness Stages
        md.append("## Customer Awareness Stages\n")
        awareness = message_map.get('awareness_stages', {})

        stages = [
            ('unaware', 'Unaware'),
            ('problem_aware', 'Problem Aware'),
            ('solution_aware', 'Solution Aware'),
            ('product_aware', 'Product Aware'),
            ('most_aware', 'Most Aware')
        ]

        for stage_key, stage_name in stages:
            stage_data = awareness.get(stage_key, {})
            if stage_data:
                md.append(f"### {stage_name}")
                md.append(f"\n**Key Phrases:**")
                for indicator in stage_data.get('indicators', []):
                    md.append(f"- {indicator}")
                md.append(f"\n**Example Quotes:**")
                for quote in stage_data.get('quotes', []):
                    md.append(f"> {quote}")
                md.append("")

        # Ad-Ready Hooks
        md.append("## Ad-Ready Hooks\n")
        hooks = message_map.get('ad_ready_hooks', {})
        for stage, hook_list in hooks.items():
            md.append(f"### {stage.replace('_', ' ').title()}")
            for hook in hook_list:
                md.append(f"- {hook}")
            md.append("")

        # Body Copy Frameworks
        md.append("## Body Copy Frameworks\n")
        for framework in message_map.get('body_copy_frameworks', []):
            md.append(f"### {framework.get('framework_name', 'N/A')}")
            md.append(f"**Target Awareness:** {framework.get('target_awareness', 'N/A')}")
            md.append(f"\n**Example:**")
            md.append(f"> {framework.get('example', 'N/A')}")
            md.append("")

        # Call to Actions
        md.append("## Call to Action Suggestions\n")
        for cta in message_map.get('call_to_actions', []):
            md.append(f"- {cta}")
        md.append("")

        # Objection Handlers
        md.append("## Objection Handlers\n")
        for obj in message_map.get('objection_handlers', []):
            md.append(f"**Objection:** {obj.get('objection', 'N/A')}")
            md.append(f"**Response:** {obj.get('response', 'N/A')}")
            md.append("")

        return "\n".join(md)

    def save_as_html(
        self,
        message_map: Dict[str, Any],
        filename: str = None
    ) -> str:
        """
        Save message map as HTML file.

        Args:
            message_map: Message map to save
            filename: Optional custom filename

        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"message_map_{timestamp}.html"

        filepath = os.path.join(self.output_dir, filename)

        html = self._generate_html(message_map)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"Message map saved to: {filepath}")
        return filepath

    def _generate_html(self, message_map: Dict[str, Any]) -> str:
        """Generate HTML formatted message map."""
        summary = message_map.get('executive_summary', {})

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Customer Language Message Map</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; border-left: 4px solid #3498db; padding-left: 10px; }}
        h3 {{ color: #7f8c8d; }}
        .summary {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .quote {{
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin: 10px 0;
            font-style: italic;
            color: #555;
        }}
        .hook {{
            background: #e8f8f5;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 3px solid #27ae60;
        }}
        .pain-point {{
            background: #fdedec;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 3px solid #e74c3c;
        }}
        .emotion {{
            background: #fff9e6;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 3px solid #f39c12;
        }}
        .framework {{
            background: #f0f8ff;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            border: 1px solid #3498db;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 5px;
        }}
        .badge-high {{ background: #e74c3c; color: white; }}
        .badge-medium {{ background: #f39c12; color: white; }}
        .badge-low {{ background: #27ae60; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Customer Language Message Map</h1>
        <p><strong>Generated:</strong> {message_map.get('generated_at', 'N/A')}</p>

        <div class="summary">
            <h2>Executive Summary</h2>
            <p><strong>Top Pain Point:</strong> {summary.get('top_pain_point', 'N/A')}</p>
            <p><strong>Dominant Emotion:</strong> {summary.get('dominant_emotion', 'N/A')}</p>
            <p><strong>Primary Desire:</strong> {summary.get('primary_desire', 'N/A')}</p>
            <p><strong>Patterns Identified:</strong> {summary.get('total_emotional_patterns', 0)} emotional patterns,
               {summary.get('total_pain_points', 0)} pain points,
               {summary.get('total_desire_triggers', 0)} desire triggers</p>
        </div>

        <h2>Key Insights</h2>
        <ul>
"""

        for insight in message_map.get('key_insights', []):
            html += f"            <li>{insight}</li>\n"

        html += """        </ul>

        <h2>Pain Points</h2>
"""

        for pain in message_map.get('pain_points', []):
            severity = pain.get('severity', 'medium')
            html += f"""        <div class="pain-point">
            <h3>{pain.get('pain_point', 'N/A')} <span class="badge badge-{severity}">{severity}</span></h3>
            <p><strong>Customer Quotes:</strong></p>
"""
            for quote in pain.get('customer_quotes', []):
                html += f'            <div class="quote">{quote}</div>\n'
            html += "        </div>\n"

        html += """
        <h2>Ad-Ready Hooks</h2>
"""

        for stage, hooks in message_map.get('ad_ready_hooks', {}).items():
            html += f"        <h3>{stage.replace('_', ' ').title()}</h3>\n"
            for hook in hooks:
                html += f'        <div class="hook">{hook}</div>\n'

        html += """
        <h2>Body Copy Frameworks</h2>
"""

        for framework in message_map.get('body_copy_frameworks', []):
            html += f"""        <div class="framework">
            <h3>{framework.get('framework_name', 'N/A')}</h3>
            <p><strong>Target Awareness:</strong> {framework.get('target_awareness', 'N/A')}</p>
            <p><strong>Example:</strong></p>
            <div class="quote">{framework.get('example', 'N/A')}</div>
        </div>
"""

        html += """    </div>
</body>
</html>"""

        return html
