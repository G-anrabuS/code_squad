"""
API endpoints for codebase analysis.
"""
from io import BytesIO
import logging
import os
import uuid
from typing import Dict, Any, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from app.services.analysis_errors import AnalysisError
from app.services.analysis_pipeline import run_full_analysis
from app.services.embedding_service import ingest_repository_to_qdrant
from app.services.clone_service import clone_repo_from_url
from app.services.download_service import render_markdown, render_pdf_bytes, render_json
from app.services.chat_service import rag_chat
from app.services.qdrant_service import build_repo_context


router = APIRouter(tags=["analysis"])
logger = logging.getLogger(__name__)

# Store for background task results
analysis_results: Dict[str, Dict[str, Any]] = {}


class AnalysisRequest(BaseModel):
    """Request model for codebase analysis."""
    repo_path: Optional[str] = None
    repo_url: Optional[str] = None
    repo_name: Optional[str] = None
    branch: Optional[str] = 'main'
    export_format: Optional[str] = 'json'


class DownloadRequest(BaseModel):
    """Request model for report download."""
    report: Dict[str, Any]
    format: Optional[str] = 'pdf'
    filename: Optional[str] = None


class ChatRequest(BaseModel):
    """Request model for RAG chatbot."""
    query: str
    repo_path: Optional[str] = None
    repo_url: Optional[str] = None
    branch: Optional[str] = 'main'


class AnalysisResponse(BaseModel):
    """Response model for analysis."""
    status: str
    data: Optional[Dict[str, Any]] = None
    error_type: Optional[str] = None
    message: Optional[str] = None
    task_id: Optional[str] = None


class EmbedRequest(BaseModel):
    """Request model for codebase embedding ingestion."""
    repo_path: str
    model: Optional[str] = None
    collection_name: Optional[str] = None


class EmbedResponse(BaseModel):
    """Response model for codebase embedding ingestion."""
    status: str
    message: Optional[str] = None
    ingested_points: Optional[int] = None
    collection_name: Optional[str] = None
    model: Optional[str] = None


@router.post("/embed", response_model=EmbedResponse)
async def embed_codebase(request: EmbedRequest) -> EmbedResponse:
    """
    Ingest codebase chunks into Qdrant using local embeddings.

    - **repo_path**: Path to the repository to index
    - **model**: Optional embedding model name
    - **collection_name**: Optional Qdrant collection name
    """
    try:
        if not os.path.exists(request.repo_path):
            raise HTTPException(status_code=400, detail=f"Repository path not found: {request.repo_path}")

        if not os.path.isdir(request.repo_path):
            raise HTTPException(status_code=400, detail=f"Path is not a directory: {request.repo_path}")

        result = ingest_repository_to_qdrant(
            repo_path=request.repo_path,
            collection_name=request.collection_name,
            model=request.model,
        )

        return EmbedResponse(
            status="success",
            message="Codebase successfully indexed into Qdrant.",
            ingested_points=result["ingested_points"],
            collection_name=result["collection_name"],
            model=result["model"],
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Embed endpoint failed unexpectedly")
        raise HTTPException(
            status_code=500,
            detail="Embedding ingestion failed unexpectedly.",
        )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_codebase(request: AnalysisRequest):
    """
    Analyze a codebase and return comprehensive findings.

    - **repo_path**: Local repository path to analyze
    - **repo_url**: GitHub repository URL to clone and analyze
    - **export_format**: 'json' or 'markdown'
    """
    try:
        repo_path = _resolve_repo_path(request)

        report = await run_full_analysis(repo_path)
        report_data = report.dict()
        report_data['type'] = request.export_format or 'json'

        if request.export_format == 'markdown':
            return AnalysisResponse(
                status='success',
                data={'markdown': render_markdown(report_data), 'type': 'markdown'}
            )

        return AnalysisResponse(
            status='success',
            data=report_data,
        )
    except AnalysisError as exc:
        return JSONResponse(status_code=exc.http_status, content=exc.to_response())
    except HTTPException:
        raise
    except Exception:
        logger.exception("Analysis endpoint failed unexpectedly")
        error = AnalysisError(
            error_type="unknown_error",
            message="Analysis failed unexpectedly.",
            http_status=500,
        )
        return JSONResponse(status_code=error.http_status, content=error.to_response())


@router.post("/download")
async def download_report(request: DownloadRequest):
    """Render an analysis report for download in PDF, markdown, or JSON."""
    try:
        output_format = (request.format or 'pdf').lower()
        filename = request.filename or f"analysis_report.{output_format}"

        if output_format == 'pdf':
            payload = render_pdf_bytes(request.report)
            return StreamingResponse(
                BytesIO(payload),
                media_type='application/pdf',
                headers={'Content-Disposition': f'attachment; filename="{filename}"'},
            )

        if output_format == 'markdown':
            payload = render_markdown(request.report).encode('utf-8')
            return StreamingResponse(
                BytesIO(payload),
                media_type='text/markdown',
                headers={'Content-Disposition': f'attachment; filename="{filename}"'},
            )

        payload = render_json(request.report).encode('utf-8')
        return StreamingResponse(
            BytesIO(payload),
            media_type='application/json',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )
    except Exception:
        logger.exception("Download endpoint failed unexpectedly")
        raise HTTPException(
            status_code=500,
            detail="Report download failed unexpectedly.",
        )


@router.post("/chat")
async def chat_codebase(request: ChatRequest) -> Dict[str, Any]:
    """Ask a question against a repository using Retrieval-Augmented Generation."""
    try:
        repo_path = _resolve_repo_path(request)
        repo_context = build_repo_context(repo_path)

        ingest_repository_to_qdrant(repo_path)

        answer = await rag_chat(
            query=request.query,
            repo_context=repo_context,
            repo_id=repo_context.get('repo_id'),
        )

        return {
            'status': 'success',
            'result': answer,
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Chat endpoint failed unexpectedly")
        raise HTTPException(
            status_code=500,
            detail="Chat request failed unexpectedly.",
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
        repo_path = _resolve_repo_path(request)

        task_id = str(uuid.uuid4())

        background_tasks.add_task(
            _run_analysis_background,
            task_id=task_id,
            repo_path=repo_path,
            export_format=request.export_format,
        )

        return {
            'status': 'started',
            'task_id': task_id,
            'message': f'Analysis started. Check /analysis/result/{task_id} for results',
        }
    except HTTPException:
        raise
    except AnalysisError as exc:
        return JSONResponse(status_code=exc.http_status, content=exc.to_response())
    except Exception:
        logger.exception("Background analysis enqueue failed unexpectedly")
        error = AnalysisError(
            error_type="unknown_error",
            message="Failed to start background analysis.",
            http_status=500,
        )
        return JSONResponse(status_code=error.http_status, content=error.to_response())


@router.get("/analysis/result/{task_id}")
async def get_analysis_result(task_id: str) -> Dict[str, Any]:
    """Get results of background analysis task."""
    if task_id not in analysis_results:
        return {
            'status': 'error',
            'error_type': 'not_found',
            'message': f'Task {task_id} not found',
        }
    return analysis_results[task_id]


@router.get("/analysis/summary/{task_id}")
async def get_analysis_summary(task_id: str) -> Dict[str, Any]:
    """Get summary of analysis without full details."""
    if task_id not in analysis_results:
        raise HTTPException(status_code=404, detail=f'Task {task_id} not found')

    result = analysis_results[task_id]
    if result['status'] != 'success':
        return {
            'status': result['status'],
            'error_type': result.get('error_type'),
            'message': result.get('message'),
        }

    report = result['data']
    return {
        'status': 'success',
        'timestamp': report.get('timestamp'),
        'repository_info': {
            'total_files': report['repository_info']['total_files'],
            'project_type': report['repository_info']['project_type'],
            'tech_stack': report['repository_info']['tech_stack'],
        },
        'code_quality_score': report.get('overall_score', 0),
        'security_level': report.get('security_review', {}).get('severity', 'UNKNOWN'),
        'priority_actions': report.get('priority_fixes', [])[:5],
    }


def _resolve_repo_path(request: AnalysisRequest) -> str:
    if request.repo_url:
        return clone_repo_from_url(request.repo_url, branch=request.branch)

    if request.repo_path:
        if not os.path.exists(request.repo_path):
            raise HTTPException(status_code=400, detail=f"Repository path not found: {request.repo_path}")
        if not os.path.isdir(request.repo_path):
            raise HTTPException(status_code=400, detail=f"Path is not a directory: {request.repo_path}")
        return request.repo_path

    raise HTTPException(status_code=400, detail="repo_path or repo_url is required for analysis.")


async def _run_analysis_background(task_id: str, repo_path: str, export_format: str = 'json') -> None:
    """Run analysis in background and store results."""
    try:
        analysis_results[task_id] = {'status': 'processing'}

        report = await run_full_analysis(repo_path)
        if export_format == 'markdown':
            report_data = {'markdown': render_markdown(report.dict()), 'type': 'markdown'}
        else:
            report_data = report.dict()
            report_data['type'] = 'json'

        analysis_results[task_id] = {
            'status': 'success',
            'data': report_data,
            'timestamp': report_data.get('timestamp'),
        }
    except AnalysisError as exc:
        analysis_results[task_id] = exc.to_response()
    except Exception:
        logger.exception("Background analysis failed unexpectedly")
        analysis_results[task_id] = AnalysisError(
            error_type='unknown_error',
            message='Background analysis failed unexpectedly.',
            http_status=500,
        ).to_response()
