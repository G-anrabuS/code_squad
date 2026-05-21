"""
Quick Start Guide - Testing the Analysis System
"""

# 1. INSTALLATION
# ===============
# pip install -r requirements.txt

# 2. START BACKEND
# ================
# uvicorn app.main:app --reload
# Server: http://localhost:8000
# Docs: http://localhost:8000/docs

# 3. API ENDPOINTS
# ================

# 3.1 Synchronous Analysis (Simple, Blocking)
# =============================================
POST http://localhost:8000/analysis/analyze
Content-Type: application/json

{
  "repo_path": "c:\\Users\\janna\\OneDrive\\Desktop\\code_squad\\fastapi_backend",
  "export_format": "json"
}

# Response: Complete analysis report immediately
# Note: For large repos, this might take several seconds


# 3.2 Asynchronous Analysis (For Large Repos)
# =============================================
POST http://localhost:8000/analysis/analyze/background
Content-Type: application/json

{
  "repo_path": "c:\\Users\\janna\\OneDrive\\Desktop\\code_squad\\fastapi_backend",
  "export_format": "json"
}

# Response:
# {
#   "status": "started",
#   "task_id": "550e8400-e29b-41d4-a716-446655440000",
#   "message": "Analysis started. Check /analysis/result/{task_id} for results"
# }


# 3.3 Check Background Task Results
# ==================================
GET http://localhost:8000/analysis/result/550e8400-e29b-41d4-a716-446655440000

# Response: 
# {
#   "status": "processing"  # or "complete", "error"
# }
# OR
# {
#   "status": "complete",
#   "report": { ... full report ... },
#   "timestamp": "2024-01-15T10:30:00"
# }


# 3.4 Get Quick Summary
# ======================
GET http://localhost:8000/analysis/summary/550e8400-e29b-41d4-a716-446655440000

# Response: Quick summary without full details
# {
#   "status": "complete",
#   "repository_info": {
#     "total_files": 45,
#     "project_type": "Backend API",
#     "tech_stack": ["Python", "FastAPI", "PostgreSQL"]
#   },
#   "code_quality_score": 0.72,
#   "security_level": "MEDIUM",
#   "priority_actions": [...]
# }


# 4. ANALYSIS REPORT STRUCTURE
# =============================

{
  "status": "success",
  "report": {
    "timestamp": "2024-01-15T10:30:00.123456",
    
    # Repository Overview
    "repository_info": {
      "total_files": 45,
      "total_lines": 12500,
      "project_type": "Backend API",
      "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
      "important_files": [
        "app/main.py",
        "app/api/repos.py",
        "requirements.txt"
      ]
    },
    
    # Project Summary
    "project_summary": {
      "overview": "This is a Backend API project...",
      "major_modules": ["API Module", "Authentication", "Data Models"],
      "architecture_flow": "HTTP Request → Router → Service → Database → Response",
      "technologies_used": ["Python", "FastAPI", "PostgreSQL"],
      "integrations": ["GitHub OAuth"],
      "backend_structure": { ... },
      "frontend_structure": { ... }
    },
    
    # Architecture Analysis
    "architecture_analysis": {
      "current_pattern": "REST API",
      "maturity": "Established",
      "complexity": "Moderate",
      "folder_structure_issues": [
        "No clear data model layer",
        "Business logic not separated..."
      ],
      "modularization_opportunities": [
        "Extract authentication into service",
        "Create caching layer"
      ],
      "refactoring_opportunities": [ ... ],
      "improved_architecture": { ... }
    },
    
    # Code Quality
    "code_quality_assessment": {
      "overall_score": 0.72,        # 72%
      "maintainability": 0.68,
      "scalability": 0.65,
      "readability": 0.78,
      "modularity": 0.70,
      "design_consistency": 0.75,
      "technical_debt": [
        "Large codebase without modularization",
        "Missing test files"
      ],
      "potential_bugs": [
        "Missing centralized error handling",
        "No input validation detected"
      ],
      "anti_patterns": [
        "Possible god object pattern",
        "Hardcoded configuration"
      ]
    },
    
    # Performance Analysis
    "performance_analysis": {
      "bottlenecks": [
        "Potential N+1 database queries",
        "Missing database query optimization"
      ],
      "inefficient_patterns": [ ... ],
      "memory_issues": [ ... ],
      "async_handling_score": 0.5,
      "caching_opportunities": [
        "Implement Redis for caching",
        "Cache expensive queries"
      ],
      "database_issues": [ ... ],
      "optimization_strategies": [ ... ],
      "priority_fixes": [
        ["Query optimization", "HIGH"],
        ["Add caching layer", "HIGH"]
      ]
    },
    
    # Security Analysis
    "security_assessment": {
      "severity_level": "MEDIUM",   # CRITICAL, HIGH, MEDIUM, LOW
      "critical_vulnerabilities": [],
      "high_risk_issues": [
        "No authentication mechanism detected",
        "Missing input validation",
        "No rate limiting"
      ],
      "medium_risk_issues": [
        "No logging infrastructure",
        "Missing error handling"
      ],
      "dependency_risks": [
        "Run 'pip audit' to check for vulnerabilities"
      ],
      "authentication_mechanisms": ["JWT-based"],
      "api_security_score": 0.65,
      "data_handling_issues": [ ... ],
      "compliance_risks": [ ... ]
    },
    
    # Recommendations
    "recommendations": {
      "architecture_improvements": [ ... ],
      "code_quality_fixes": [ ... ],
      "performance_optimizations": [ ... ],
      "security_fixes": [ ... ]
    },
    
    # Priority Actions (Top 10)
    "priority_actions": [
      "🔴 CRITICAL: Fix hardcoded secrets in source code",
      "🔴 HIGH: Implement input validation on all endpoints",
      "🟠 PERFORMANCE: Optimize N+1 database queries",
      "🟡 REFACTOR: Break down large monolithic files",
      "🟡 TECHNICAL DEBT: Add missing test files"
    ]
  }
}


# 5. PYTHON USAGE
# ===============

import asyncio
from app.services.analysis_pipeline import AnalysisPipeline

async def main():
    pipeline = AnalysisPipeline()
    
    # Analyze repository
    repo_path = "c:\\Users\\janna\\OneDrive\\Desktop\\code_squad\\fastapi_backend"
    report = await pipeline.analyze_repository(repo_path)
    
    # Access findings
    print(f"Project Type: {report.repository_info['project_type']}")
    print(f"Tech Stack: {report.repository_info['tech_stack']}")
    print(f"Code Quality: {report.code_quality_assessment['overall_score']:.0%}")
    print(f"Security Level: {report.security_assessment['severity_level']}")
    
    # Export as markdown
    from app.services.report_generator import ReportGenerator
    generator = ReportGenerator()
    markdown = generator.to_markdown(report)
    
    # Save to file
    with open("analysis_report.md", "w") as f:
        f.write(markdown)
    
    print("Report saved to analysis_report.md")

asyncio.run(main())


# 6. CURL EXAMPLES
# ================

# Analyze repository (synchronous)
curl -X POST "http://localhost:8000/analysis/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "c:\\\\Users\\\\janna\\\\OneDrive\\\\Desktop\\\\code_squad\\\\fastapi_backend",
    "export_format": "json"
  }'

# Analyze in background
curl -X POST "http://localhost:8000/analysis/analyze/background" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "c:\\\\Users\\\\janna\\\\OneDrive\\\\Desktop\\\\code_squad\\\\fastapi_backend"
  }'

# Get results (replace task_id)
curl "http://localhost:8000/analysis/result/550e8400-e29b-41d4-a716-446655440000"

# Get summary
curl "http://localhost:8000/analysis/summary/550e8400-e29b-41d4-a716-446655440000"


# 7. TEST SCENARIOS
# =================

# Scenario 1: Analyze this backend
repo_path = "c:\\Users\\janna\\OneDrive\\Desktop\\code_squad\\fastapi_backend"

# Scenario 2: Analyze Flutter frontend
repo_path = "c:\\Users\\janna\\OneDrive\\Desktop\\code_squad\\flutter_frontend"

# Scenario 3: Analyze full workspace
repo_path = "c:\\Users\\janna\\OneDrive\\Desktop\\code_squad"


# 8. EXPECTED OUTPUTS FOR DIFFERENT REPOS
# ========================================

# For Backend (FastAPI):
# - Project Type: "Backend API"
# - Tech Stack: ["Python", "FastAPI", "PostgreSQL"]
# - Architecture: "REST API"
# - Security Focus: Authentication, Input Validation, CORS

# For Frontend (Flutter):
# - Project Type: "Frontend Application"
# - Tech Stack: ["Dart", "Flutter"]
# - Architecture: "Mobile/Web App"
# - Performance Focus: Re-renders, Bundle size

# For Full Workspace:
# - Project Type: "Mixed Project"
# - Tech Stack: Multiple technologies
# - Modules: Both backend and frontend

