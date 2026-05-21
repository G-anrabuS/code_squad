# 🤖 CodeSquad: Codebase Intelligence & Architecture Analysis System

A sophisticated multi-agent backend system that automatically analyzes codebases using AI-powered specialized agents. The system provides deep insights into code quality, architecture, performance, and security.

## 🎯 Overview

CodeSquad implements a 7-agent analysis pipeline that examines codebases from multiple perspectives:

1. **Codebase Analyzer** - Traverses repository, identifies files, detects tech stack
2. **Summary Agent** - Generates comprehensive project overview
3. **Judge Agent** - Reviews code quality and maintainability
4. **Architect Agent** - Analyzes architecture and suggests improvements
5. **Performance Agent** - Identifies bottlenecks and optimization opportunities
6. **Security Agent** - Scans for vulnerabilities and compliance issues
7. **Report Generator** - Creates structured final report

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Analysis Pipeline Orchestrator         │  │
│  └──────────────────────────────────────────────────┘  │
│                        │                                │
│   ┌────────────────────┼────────────────────┐          │
│   │                    │                    │          │
│   ▼                    ▼                    ▼          │
│ ┌──────────┐      ┌──────────┐      ┌──────────┐     │
│ │ Codebase │      │ Summary  │      │  Judge   │     │
│ │ Analyzer │      │  Agent   │      │  Agent   │     │
│ └──────────┘      └──────────┘      └──────────┘     │
│   ┌──────────┐      ┌──────────┐      ┌──────────┐     │
│   │Architect │      │Performance    │ Security │     │
│   │  Agent   │      │   Agent      │  Agent    │     │
│   └──────────┘      └──────────┘      └──────────┘     │
│                        │                                │
│                        ▼                                │
│                  ┌──────────────┐                      │
│                  │ Report       │                      │
│                  │ Generator    │                      │
│                  └──────────────┘                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 🚀 API Endpoints

### 1. Synchronous Analysis (Blocking)
```http
POST /analysis/analyze
Content-Type: application/json

{
  "repo_path": "/path/to/repository",
  "export_format": "json"  # or "markdown"
}

Response:
{
  "status": "success",
  "report": {
    "timestamp": "2024-01-15T10:30:00",
    "repository_info": {...},
    "project_summary": {...},
    "architecture_analysis": {...},
    "code_quality_assessment": {...},
    "performance_analysis": {...},
    "security_assessment": {...},
    "recommendations": {...},
    "priority_actions": [...]
  }
}
```

### 2. Asynchronous Analysis (Background Task)
```http
POST /analysis/analyze/background
Content-Type: application/json

{
  "repo_path": "/path/to/repository",
  "export_format": "json"
}

Response:
{
  "status": "started",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Analysis started. Check /analysis/result/{task_id} for results"
}
```

### 3. Get Analysis Results
```http
GET /analysis/result/{task_id}

Response:
{
  "status": "complete",  # or "processing", "error"
  "report": {...},
  "timestamp": "2024-01-15T10:30:00"
}
```

### 4. Get Analysis Summary
```http
GET /analysis/summary/{task_id}

Response:
{
  "status": "complete",
  "repository_info": {
    "total_files": 45,
    "project_type": "Backend API",
    "tech_stack": ["Python", "FastAPI", "PostgreSQL"]
  },
  "code_quality_score": 0.72,
  "security_level": "MEDIUM",
  "priority_actions": [...]
}
```

## 📊 Report Structure

The comprehensive report includes:

### Repository Information
- Total files and lines of code
- Project type detection
- Technology stack identified
- Important/prioritized files

### Project Summary
- Project overview and purpose
- Major modules and components
- Architecture flow description
- Key integrations
- Backend/frontend structure
- Execution pipeline

### Architecture Analysis
- Current architecture pattern
- Maturity and complexity assessment
- Folder structure evaluation
- Modularization opportunities
- Service separation suggestions
- Refactoring recommendations
- Improved architecture proposal

### Code Quality Assessment
- Quality scores (0.0-1.0) for:
  - Maintainability
  - Scalability
  - Readability
  - Modularity
  - Design consistency
- Technical debt identification
- Potential bugs
- Anti-patterns detected

### Performance Analysis
- Performance bottlenecks
- Inefficient coding patterns
- Memory issues
- Async/await handling assessment
- Caching opportunities
- Database optimization suggestions
- Prioritized fixes by impact

### Security Assessment
- Severity level (CRITICAL, HIGH, MEDIUM, LOW)
- Critical vulnerabilities
- High-risk issues
- Medium-risk issues
- Dependency vulnerability assessment
- Authentication mechanisms analysis
- API security score
- Data handling review
- Compliance risks

### Recommendations
- By category: Architecture, Performance, Code Quality, Security
- Prioritized action list
- Implementation roadmap

## 🛠️ Installation

1. **Install dependencies:**
```bash
cd fastapi_backend
pip install -r requirements.txt
```

2. **Run the server:**
```bash
uvicorn app.main:app --reload
```

Server starts on `http://localhost:8000`

## 📝 Usage Examples

### Example 1: Analyze Local Project
```python
import asyncio
from app.services.analysis_pipeline import AnalysisPipeline

async def analyze_my_project():
    pipeline = AnalysisPipeline()
    report = await pipeline.analyze_repository("/path/to/my/project")
    
    # Access specific findings
    print(f"Code Quality: {report.code_quality_assessment['overall_score']:.0%}")
    print(f"Security Level: {report.security_assessment['severity_level']}")
    print(f"Priority Actions: {report.priority_actions}")

asyncio.run(analyze_my_project())
```

### Example 2: Export as Markdown
```python
from app.services.analysis_pipeline import AnalysisPipeline
from app.services.report_generator import ReportGenerator

async def export_markdown_report():
    pipeline = AnalysisPipeline()
    report = await pipeline.analyze_repository("/path/to/project")
    
    generator = ReportGenerator()
    markdown = generator.to_markdown(report)
    
    with open("analysis_report.md", "w") as f:
        f.write(markdown)

asyncio.run(export_markdown_report())
```

### Example 3: Via HTTP API
```bash
# Synchronous analysis (wait for results)
curl -X POST "http://localhost:8000/analysis/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/Users/janna/projects/myapp",
    "export_format": "json"
  }'

# Asynchronous analysis (returns task_id)
curl -X POST "http://localhost:8000/analysis/analyze/background" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/Users/janna/projects/myapp",
    "export_format": "markdown"
  }'

# Get results later
curl "http://localhost:8000/analysis/result/550e8400-e29b-41d4-a716-446655440000"
```

## 🧠 Agent Details

### Codebase Analyzer
- Traverses entire repository
- Identifies file organization
- Detects technology stack
- Extracts dependencies
- Finds important/prioritized files
- Assesses modular structure

### Summary Agent
- Generates project overview
- Identifies major modules
- Describes architecture flow
- Lists technologies and integrations
- Analyzes backend/frontend structure
- Outlines execution pipeline

### Judge Agent
- Scores code quality (0-100%)
- Evaluates maintainability
- Assesses scalability potential
- Rates readability
- Checks modularity
- Identifies technical debt
- Detects potential bugs
- Finds anti-patterns

### Architect Agent
- Analyzes current architecture
- Assesses maturity level
- Evaluates complexity
- Suggests folder restructuring
- Recommends modularization
- Proposes service separation
- Suggests design patterns
- Identifies refactoring opportunities
- Proposes improved architecture

### Performance Agent
- Identifies bottlenecks
- Finds inefficient patterns
- Detects memory issues
- Assesses async handling
- Suggests caching opportunities
- Reviews database queries
- Generates optimization strategies
- Prioritizes fixes by impact

### Security Agent
- Finds critical vulnerabilities
- Identifies high-risk issues
- Assesses API security (0-100%)
- Reviews authentication
- Checks input validation
- Analyzes data handling
- Assesses dependency risks
- Identifies compliance risks
- Prioritizes fixes by severity

## 🔧 Advanced Configuration

### Customize File Extensions
Edit `CodebaseParser.CODE_EXTENSIONS` in `codebase_parser.py`:
```python
CODE_EXTENSIONS = {
    '.py', '.ts', '.tsx', '.js', '.jsx',
    # Add more extensions...
}
```

### Adjust Skip Directories
Edit `CodebaseParser.SKIP_DIRS`:
```python
SKIP_DIRS = {
    '.git', '__pycache__', 'node_modules',
    # Add more directories to skip...
}
```

### Modify Agent Scoring
Edit individual agent files to adjust scoring algorithms and thresholds.

## 📈 Scaling for Large Codebases

For very large repositories:

1. **Use background analysis:**
   ```python
   POST /analysis/analyze/background
   ```

2. **Increase timeouts in FastAPI:**
   ```python
   app = FastAPI()
   # Add config for longer running tasks
   ```

3. **Consider caching results:**
   - Implement Redis for result caching
   - Store analysis results in database

## 🔐 Security Considerations

- Sanitize file paths to prevent directory traversal
- Run analysis in isolated environment
- Limit repository size
- Implement rate limiting on analysis endpoints
- Don't expose full file contents in reports

## 📚 Example Analysis Report

See `example_report.md` for a sample comprehensive analysis output.

## 🚀 Future Enhancements

- [ ] Integration with LangChain for LLM-powered analysis
- [ ] Custom agent creation
- [ ] LLM-powered recommendations
- [ ] Automated refactoring suggestions
- [ ] Pull request generation
- [ ] GitHub/GitLab integration
- [ ] CI/CD pipeline integration
- [ ] Trend analysis over time
- [ ] Team collaboration features
- [ ] Custom scoring rules

## 📞 Support

For issues or questions, check the logs:
```bash
tail -f fastapi_backend.log
```

## 📄 License

MIT License

---

**Built with ❤️ using FastAPI and Python**
