"""
API endpoints for codebase analysis.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.analysis_pipeline import run_full_analysis, run_analysis_export
from app.services.report_generator import ReportGenerator
import os


router = APIRouter(tags=["analysis"])

# Store for background task results
analysis_results: Dict[str, Dict[str, Any]] = {}


class AnalysisRequest(BaseModel):
    """Request model for codebase analysis."""
    repo_path: str
    export_format: Optional[str] = 'json'


class AnalysisResponse(BaseModel):
    """Response model for analysis."""
    status: str
    report: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    task_id: Optional[str] = None


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_codebase(request: AnalysisRequest) -> AnalysisResponse:
    """
    Analyze a codebase and return comprehensive findings.
    
    - **repo_path**: Path to the repository to analyze
    - **export_format**: 'json' or 'markdown'
    
    Returns comprehensive analysis from all agents.
    """
    
    try:
        # Validate path exists
        if not os.path.exists(request.repo_path):
            raise HTTPException(status_code=400, detail=f"Repository path not found: {request.repo_path}")
        
        if not os.path.isdir(request.repo_path):
            raise HTTPException(status_code=400, detail=f"Path is not a directory: {request.repo_path}")
        
        # Run analysis
        report = await run_full_analysis(request.repo_path)
        
        # Export in requested format
        report_generator = ReportGenerator()
        
        if request.export_format == 'markdown':
            report_data = {
                'markdown': report_generator.to_markdown(report),
                'timestamp': report.timestamp,
                'type': 'markdown'
            }
        else:
            report_data = report_generator.to_dict(report)
            report_data['type'] = 'json'
        
        return AnalysisResponse(
            status='success',
            report=report_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        return AnalysisResponse(
            status='error',
            error=str(e)
        )


@router.post("/analyze/background")
async def analyze_codebase_background(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """
    Analyze codebase in background and return task ID.
    
    Use the returned task_id to check results with /analysis/result/{task_id}
    """
    
    try:
        # Validate path
        if not os.path.exists(request.repo_path):
            raise HTTPException(status_code=400, detail=f"Repository path not found: {request.repo_path}")
        
        # Generate task ID
        import uuid
        task_id = str(uuid.uuid4())
        
        # Add background task
        background_tasks.add_task(
            _run_analysis_background,
            task_id=task_id,
            repo_path=request.repo_path,
            export_format=request.export_format
        )
        
        return {
            'status': 'started',
            'task_id': task_id,
            'message': f'Analysis started. Check /analysis/result/{task_id} for results'
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/result/{task_id}")
async def get_analysis_result(task_id: str) -> Dict[str, Any]:
    """Get results of background analysis task."""
    
    if task_id not in analysis_results:
        return {
            'status': 'not_found',
            'error': f'Task {task_id} not found'
        }
    
    return analysis_results[task_id]


@router.get("/analysis/summary/{task_id}")
async def get_analysis_summary(task_id: str) -> Dict[str, Any]:
    """Get summary of analysis without full details."""
    
    if task_id not in analysis_results:
        raise HTTPException(status_code=404, detail=f'Task {task_id} not found')
    
    result = analysis_results[task_id]
    
    if result['status'] != 'complete':
        return {
            'status': result['status'],
            'error': result.get('error')
        }
    
    report = result['report']
    
    return {
        'status': 'complete',
        'timestamp': report.get('timestamp'),
        'repository_info': {
            'total_files': report['repository_info']['total_files'],
            'project_type': report['repository_info']['project_type'],
            'tech_stack': report['repository_info']['tech_stack'],
        },
        'code_quality_score': report['code_quality_assessment']['overall_score'],
        'security_level': report['security_assessment']['severity_level'],
        'priority_actions': report['priority_actions'][:5],
    }


# Helper function to run analysis in background
async def _run_analysis_background(task_id: str, repo_path: str, export_format: str = 'json') -> None:
    """Run analysis in background and store results."""
    
    try:
        analysis_results[task_id] = {'status': 'processing'}
        
        # Run analysis
        report = await run_full_analysis(repo_path)
        
        # Export in requested format
        report_generator = ReportGenerator()
        
        if export_format == 'markdown':
            report_data = {
                'markdown': report_generator.to_markdown(report),
                'timestamp': report.timestamp,
                'type': 'markdown'
            }
        else:
            report_data = report_generator.to_dict(report)
            report_data['type'] = 'json'
        
        # Store result
        analysis_results[task_id] = {
            'status': 'complete',
            'report': report_data,
            'timestamp': report.timestamp,
        }
    
    except Exception as e:
        analysis_results[task_id] = {
            'status': 'error',
            'error': str(e)
        }
