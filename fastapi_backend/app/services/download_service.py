import json
from io import BytesIO
from typing import Any, Dict

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.units import inch


def render_markdown(report: Dict[str, Any]) -> str:
    lines = [
        f"# Repository Analysis Report",
        "",
        f"**Repo ID:** {report.get('repo_id', '')}",
        f"**Generated:** {report.get('timestamp', '')}",
        "",
        "## Repository Info",
    ]
    repo_info = report.get('repository_info', {})
    lines.extend([
        f"- Project Type: {repo_info.get('project_type', '')}",
        f"- Tech Stack: {', '.join(repo_info.get('tech_stack', []))}",
        f"- Total Files: {repo_info.get('total_files', 0)}",
        "",
        "## Summary",
        report.get('summary', {}).get('summary', ''),
        "",
        "## Priority Fixes",
    ])
    for fix in report.get('priority_fixes', []):
        lines.append(f"- {fix}")
    lines.append("")
    lines.append("## Final Recommendations")
    for rec in report.get('final_recommendations', []):
        lines.append(f"- {rec}")
    return "\n".join(lines)


def render_json(report: Dict[str, Any]) -> str:
    return json.dumps(report, indent=2)


def render_pdf_bytes(report: Dict[str, Any]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    flow = []

    flow.append(Paragraph("Repository Analysis Report", styles['Title']))
    flow.append(Spacer(1, 0.2 * inch))
    flow.append(Paragraph(f"Repo ID: {report.get('repo_id', '')}", styles['Normal']))
    flow.append(Paragraph(f"Generated: {report.get('timestamp', '')}", styles['Normal']))
    flow.append(Spacer(1, 0.3 * inch))

    repo_info = report.get('repository_info', {})
    flow.append(Paragraph("Repository Info", styles['Heading2']))
    flow.append(Paragraph(f"Project Type: {repo_info.get('project_type', '')}", styles['Normal']))
    flow.append(Paragraph(f"Tech Stack: {', '.join(repo_info.get('tech_stack', []))}", styles['Normal']))
    flow.append(Paragraph(f"Total Files: {repo_info.get('total_files', 0)}", styles['Normal']))
    flow.append(Spacer(1, 0.2 * inch))

    summary = report.get('summary', {})
    flow.append(Paragraph("Summary", styles['Heading2']))
    flow.append(Paragraph(summary.get('summary', ''), styles['Normal']))
    flow.append(Spacer(1, 0.2 * inch))

    flow.append(Paragraph("Priority Fixes", styles['Heading2']))
    for fix in report.get('priority_fixes', []):
        flow.append(Paragraph(f"• {fix}", styles['Normal']))
    flow.append(Spacer(1, 0.2 * inch))

    flow.append(Paragraph("Final Recommendations", styles['Heading2']))
    for rec in report.get('final_recommendations', []):
        flow.append(Paragraph(f"• {rec}", styles['Normal']))
    flow.append(Spacer(1, 0.2 * inch))

    doc.build(flow)
    buffer.seek(0)
    return buffer.getvalue()
