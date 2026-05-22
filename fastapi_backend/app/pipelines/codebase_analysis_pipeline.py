import asyncio
from datetime import datetime
from typing import Any, Dict, List

from app.schemas.agent_output_schema import (
    ArchitectReview,
    JudgeReview,
    PerformanceReview,
    SecurityReview,
    SummaryReview,
)
from app.schemas.report_schema import FinalAnalysisReport
from app.services.llm_service import analyze_agent
from app.services.qdrant_service import build_repo_context, ingest_repository_to_qdrant
from app.services.retriever_service import retrieve_agent_chunks

AGENT_MODEL_MAP = {
    'summary': 'gemini-1.5-mini',
    'judge': 'gemini-1.5',
    'architect': 'gemini-1.5',
    'performance': 'gemini-1.5-mini',
    'security': 'gemini-1.5-mini',
}

AGENT_NAMES = ['summary', 'judge', 'architect', 'performance', 'security']


class CodebaseAnalysisPipeline:
    """Pipeline orchestrating repository analysis using Qdrant and OpenAI."""

    async def analyze_repository(self, repo_path: str) -> FinalAnalysisReport:
        repo_context = build_repo_context(repo_path)

        ingestion_summary = ingest_repository_to_qdrant(repo_path)

        analysis_tasks = [self._run_agent(agent_name, repo_context) for agent_name in AGENT_NAMES]
        results = await asyncio.gather(*analysis_tasks)

        agent_outputs = {result['agent_name']: result['result'] for result in results}

        return self._build_final_report(repo_context, agent_outputs, ingestion_summary)

    async def _run_agent(self, agent_name: str, repo_context: Dict[str, Any]) -> Dict[str, Any]:
        chunks = retrieve_agent_chunks(agent_name, repo_context, top_k=6)
        result = await analyze_agent(
            agent_name=agent_name,
            repo_context=repo_context,
            chunks=chunks,
            model=AGENT_MODEL_MAP.get(agent_name),
        )
        return {'agent_name': agent_name, 'result': result}

    def _build_final_report(
        self,
        repo_context: Dict[str, Any],
        agent_outputs: Dict[str, Dict[str, Any]],
        ingestion_summary: Dict[str, Any],
    ) -> FinalAnalysisReport:
        summary_data = agent_outputs.get('summary', {})
        judge_data = agent_outputs.get('judge', {})
        architect_data = agent_outputs.get('architect', {})
        performance_data = agent_outputs.get('performance', {})
        security_data = agent_outputs.get('security', {})

        summary_review = SummaryReview.parse_obj({
            'agent_name': 'summary',
            'summary': summary_data.get('summary', ''),
            'findings': summary_data.get('findings', {}),
            'recommendations': summary_data.get('recommendations', []),
            'insights': summary_data.get('insights', {}),
            'severity': summary_data.get('severity'),
            'analysis_details': summary_data.get('analysis_details'),
        })

        judge_review = JudgeReview.parse_obj({
            'agent_name': 'judge',
            'summary': judge_data.get('summary', ''),
            'findings': judge_data.get('findings', {}),
            'recommendations': judge_data.get('recommendations', []),
            'insights': judge_data.get('insights', {}),
            'severity': judge_data.get('severity'),
            'analysis_details': judge_data.get('analysis_details'),
        })

        architect_review = ArchitectReview.parse_obj({
            'agent_name': 'architect',
            'summary': architect_data.get('summary', ''),
            'findings': architect_data.get('findings', {}),
            'recommendations': architect_data.get('recommendations', []),
            'insights': architect_data.get('insights', {}),
            'severity': architect_data.get('severity'),
            'analysis_details': architect_data.get('analysis_details'),
        })

        performance_review = PerformanceReview.parse_obj({
            'agent_name': 'performance',
            'summary': performance_data.get('summary', ''),
            'findings': performance_data.get('findings', {}),
            'recommendations': performance_data.get('recommendations', []),
            'insights': performance_data.get('insights', {}),
            'severity': performance_data.get('severity'),
            'analysis_details': performance_data.get('analysis_details'),
        })

        security_review = SecurityReview.parse_obj({
            'agent_name': 'security',
            'summary': security_data.get('summary', ''),
            'findings': security_data.get('findings', {}),
            'recommendations': security_data.get('recommendations', []),
            'insights': security_data.get('insights', {}),
            'severity': security_data.get('severity'),
            'analysis_details': security_data.get('analysis_details'),
        })

        priority_fixes = []
        priority_fixes.extend(judge_review.recommendations[:3])
        priority_fixes.extend(performance_review.recommendations[:3])
        priority_fixes.extend(security_review.recommendations[:3])
        priority_fixes = [fix for fix in priority_fixes if fix]

        final_recommendations = []
        final_recommendations.extend(summary_review.recommendations[:2])
        final_recommendations.extend(architect_review.recommendations[:2])
        final_recommendations.extend(judge_review.recommendations[:2])
        final_recommendations.extend(performance_review.recommendations[:2])
        final_recommendations.extend(security_review.recommendations[:2])
        final_recommendations = [rec for rec in final_recommendations if rec]

        overall_score = 0.0
        if isinstance(judge_review.findings.get('code_quality_score'), (int, float)):
            overall_score = float(judge_review.findings.get('code_quality_score'))
        if overall_score <= 0:
            overall_score = 70.0

        return FinalAnalysisReport(
            repo_id=repo_context.get('repo_id', ''),
            timestamp=datetime.now().isoformat(),
            repository_info=repo_context.get('repository_info', {}),
            repo_context={
                'project_summary': repo_context.get('project_summary', ''),
                'tech_stack': repo_context.get('tech_stack', []),
                'folder_tree': repo_context.get('folder_tree', ''),
                'important_files': repo_context.get('important_files', []),
                'entry_points': repo_context.get('entry_points', []),
                'dependency_files': repo_context.get('dependency_files', []),
                'ingestion_summary': ingestion_summary,
            },
            overall_score=overall_score,
            summary=summary_review,
            judge_review=judge_review,
            architecture_review=architect_review,
            performance_review=performance_review,
            security_review=security_review,
            priority_fixes=priority_fixes,
            improved_architecture=architect_review.findings.get('improved_architecture', {}),
            final_recommendations=final_recommendations,
        )
