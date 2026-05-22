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
from app.services.clone_service import clone_repo_from_url, cleanup_repo
from app.services.download_service import render_markdown, render_pdf_bytes, render_json
from app.services.task_tracker import (
    complete_task,
    create_task,
    fail_task,
    get_task,
    set_task_status,
    update_step,
)

router = APIRouter(tags=["analysis"])
logger = logging.getLogger(__name__)


class AnalysisRequest(BaseModel):
    """Request model for codebase analysis."""

    repo_path: Optional[str] = None
    repo_url: Optional[str] = None
    repo_name: Optional[str] = None
    branch: Optional[str] = "main"
    export_format: Optional[str] = "json"


class DownloadRequest(BaseModel):
    """Request model for report download."""

    report: Dict[str, Any]
    format: Optional[str] = "pdf"
    filename: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model for analysis."""

    status: str
    data: Optional[Dict[str, Any]] = None
    error_type: Optional[str] = None
    message: Optional[str] = None
    task_id: Optional[str] = None


class ProgressResponse(BaseModel):
    status: str
    steps: Dict[str, str]
    message: Optional[str] = None


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_codebase(request: AnalysisRequest):
    """
    Analyze a codebase and return comprehensive findings.

    - repo_path: Local repository path
    - repo_url: GitHub repository URL
    - export_format: json or markdown
    """
    try:
        repo_path, should_cleanup = _resolve_repo_path(request)

        try:
            report = await run_full_analysis(repo_path)
            report_data = report.model_dump()
            report_data["type"] = request.export_format or "json"

            if request.export_format == "markdown":
                return AnalysisResponse(
                    status="success",
                    data={
                        "markdown": render_markdown(report_data),
                        "type": "markdown",
                    },
                )

            return AnalysisResponse(
                status="success",
                data=report_data,
            )

        finally:
            if should_cleanup:
                cleanup_repo(repo_path)

    except AnalysisError as exc:
        return JSONResponse(
            status_code=exc.http_status,
            content=exc.to_response(),
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception("Analysis endpoint failed unexpectedly")
        error = AnalysisError(
            error_type="unknown_error",
            message="Analysis failed unexpectedly.",
            http_status=500,
        )
        return JSONResponse(
            status_code=error.http_status,
            content=error.to_response(),
        )


@router.post("/download")
async def download_report(request: DownloadRequest):
    """Render analysis report for download."""
    try:
        output_format = (request.format or "pdf").lower()
        filename = request.filename or f"analysis_report.{output_format}"

        if output_format == "pdf":
            payload = render_pdf_bytes(request.report)
            return StreamingResponse(
                BytesIO(payload),
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )

        if output_format == "markdown":
            payload = render_markdown(request.report).encode("utf-8")
            return StreamingResponse(
                BytesIO(payload),
                media_type="text/markdown",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )

        payload = render_json(request.report).encode("utf-8")
        return StreamingResponse(
            BytesIO(payload),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except Exception:
        logger.exception("Download endpoint failed unexpectedly")
        raise HTTPException(
            status_code=500,
            detail="Report download failed unexpectedly.",
        )


@router.post("/analyze/background")
async def analyze_codebase_background(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    """
    Analyze codebase in background.

    Returns task_id for polling.
    """
    try:
        repo_path, should_cleanup = _resolve_repo_path(request)

        task_id = str(uuid.uuid4())
        repo_name = request.repo_name or os.path.basename(repo_path)

        create_task(task_id, repo_name)

        background_tasks.add_task(
            _run_analysis_background,
            task_id=task_id,
            repo_path=repo_path,
            should_cleanup=should_cleanup,
        )

        return {
            "status": "accepted",
            "task_id": task_id,
        }

    except HTTPException:
        raise

    except AnalysisError as exc:
        return JSONResponse(
            status_code=exc.http_status,
            content=exc.to_response(),
        )

    except Exception:
        logger.exception("Background analysis enqueue failed unexpectedly")
        error = AnalysisError(
            error_type="unknown_error",
            message="Failed to start background analysis.",
            http_status=500,
        )
        return JSONResponse(
            status_code=error.http_status,
            content=error.to_response(),
        )


@router.get("/analysis/result/{task_id}")
async def get_analysis_result(task_id: str) -> Dict[str, Any]:
    """Get background analysis result."""
    task = get_task(task_id)

    if not task:
        return {
            "status": "failed",
            "message": "Invalid or expired task id.",
        }

    if task["status"] in {"pending", "running"}:
        return {"status": "running"}

    if task["status"] == "completed":
        return {
            "status": "completed",
            "data": task.get("data"),
        }

    return {
        "status": "failed",
        "message": task.get("message") or "Analysis failed",
    }


@router.get("/progress/{task_id}", response_model=ProgressResponse)
async def get_analysis_progress(task_id: str) -> Dict[str, Any]:
    task = get_task(task_id)

    if not task:
        return {
            "status": "failed",
            "steps": {},
            "message": "Invalid or expired task id.",
        }

    return {
        "status": task["status"],
        "steps": task.get("steps", {}),
        "message": task.get("message"),
    }


@router.get("/analysis/summary/{task_id}")
async def get_analysis_summary(task_id: str) -> Dict[str, Any]:
    """Get summary without full details."""
    task = get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found",
        )

    if task["status"] != "completed":
        return {
            "status": task["status"],
            "message": task.get("message"),
        }

    report = task["data"]

    return {
        "status": "success",
        "timestamp": report.get("timestamp"),
        "repository_info": {
            "total_files": report["repository_info"]["total_files"],
            "project_type": report["repository_info"]["project_type"],
            "tech_stack": report["repository_info"]["tech_stack"],
        },
        "code_quality_score": report.get("overall_score", 0),
        "security_level": report.get("security_review", {}).get(
            "severity",
            "UNKNOWN",
        ),
        "priority_actions": report.get("priority_fixes", [])[:5],
    }


def _resolve_repo_path(request: AnalysisRequest) -> tuple[str, bool]:
    """
    Returns:
        (repo_path, should_cleanup)
    """
    if request.repo_url:
        repo_path = clone_repo_from_url(
            request.repo_url,
            branch=request.branch,
        )
        return repo_path, True

    if request.repo_path:
        if not os.path.exists(request.repo_path):
            raise HTTPException(
                status_code=400,
                detail=f"Repository path not found: {request.repo_path}",
            )

        if not os.path.isdir(request.repo_path):
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a directory: {request.repo_path}",
            )

        return request.repo_path, False

    raise HTTPException(
        status_code=400,
        detail="repo_path or repo_url is required.",
    )


async def _run_analysis_background(
    task_id: str,
    repo_path: str,
    should_cleanup: bool = False,
) -> None:
    """Run analysis in background."""
    try:
        set_task_status(task_id, "running")

        report = await run_full_analysis(
            repo_path,
            progress_callback=lambda step, status, message=None: _update_task_progress(
                task_id, step, status, message
            ),
        )

        report_data = report.model_dump()
        report_data["type"] = "json"

        complete_task(task_id, report_data)

    except AnalysisError as exc:
        fail_task(task_id, exc.message)

    except Exception:
        logger.exception("Background analysis failed unexpectedly")
        fail_task(task_id, "Background analysis failed unexpectedly.")

    finally:
        if should_cleanup:
            cleanup_repo(repo_path)


def _update_task_progress(
    task_id: str,
    step: str,
    status: str,
    message: Optional[str] = None,
) -> None:
    if status == "running":
        set_task_status(task_id, "running")

    update_step(task_id, step, status, message)
