"""
Analysis Pipeline - Orchestrates multi-agent codebase analysis.
"""
import asyncio
from typing import Dict, Any
from app.services.codebase_parser import CodebaseParser
from app.services.report_generator import ReportGenerator, ComprehensiveReport
from app.agents.codebase_analyzer_agent import CodebaseAnalyzerAgent
from app.agents.summary_agent import SummaryAgent
from app.agents.judge_agent import JudgeAgent
from app.agents.architect_agent import ArchitectAgent
from app.agents.performance_agent import PerformanceAgent
from app.agents.security_agent import SecurityAgent


class AnalysisPipeline:
    """Orchestrates multi-agent codebase analysis."""
    
    def __init__(self):
        self.parser = CodebaseParser
        self.report_generator = ReportGenerator()
        self.agents = {
            'codebase_analyzer': CodebaseAnalyzerAgent(),
            'summary': SummaryAgent(),
            'judge': JudgeAgent(),
            'architect': ArchitectAgent(),
            'performance': PerformanceAgent(),
            'security': SecurityAgent(),
        }
    
    async def analyze_repository(self, repo_path: str) -> ComprehensiveReport:
        """
        Run complete analysis pipeline on a repository.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            ComprehensiveReport with findings from all agents
        """
        
        print(f"🔍 Starting analysis pipeline for: {repo_path}")
        
        # Step 1: Parse codebase
        print("📂 Parsing codebase structure...")
        parser = self.parser(repo_path)
        codebase_data = parser.parse()
        
        print(f"   ✓ Found {codebase_data.get('total_files', 0)} files")
        print(f"   ✓ Tech Stack: {', '.join(codebase_data.get('tech_stack', []))}")
        
        # Step 2: Run all agents in parallel
        print("🤖 Running analysis agents...")
        agents_findings = await self._run_agents(codebase_data)
        
        # Step 3: Generate report
        print("📝 Generating final report...")
        report = self.report_generator.generate_report(agents_findings, codebase_data)
        
        print("✅ Analysis complete!")
        
        return report
    
    async def _run_agents(self, codebase_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all agents concurrently."""
        
        tasks = {
            agent_name: agent.analyze(codebase_data)
            for agent_name, agent in self.agents.items()
        }
        
        results = {}
        for agent_name, task in tasks.items():
            print(f"   ↪ Running {agent_name}...")
            response = await task
            results[agent_name] = {
                'findings': response.findings,
                'summary': response.summary,
                'recommendations': response.recommendations,
                'severity': response.severity,
            }
            print(f"   ✓ {agent_name} complete")
        
        return results
    
    async def analyze_and_export(self, repo_path: str, export_format: str = 'json') -> Dict[str, Any]:
        """
        Analyze repository and export in specified format.
        
        Args:
            repo_path: Path to repository
            export_format: 'json', 'markdown', or 'dict'
            
        Returns:
            Analysis report in specified format
        """
        
        report = await self.analyze_repository(repo_path)
        
        if export_format == 'json':
            return self.report_generator.to_dict(report)
        elif export_format == 'markdown':
            return {'markdown': self.report_generator.to_markdown(report)}
        else:
            return self.report_generator.to_dict(report)


# Convenience functions for API endpoints
async def run_full_analysis(repo_path: str) -> ComprehensiveReport:
    """Run full codebase analysis."""
    pipeline = AnalysisPipeline()
    return await pipeline.analyze_repository(repo_path)


async def run_analysis_export(repo_path: str, format_type: str = 'json') -> Dict[str, Any]:
    """Run analysis and export in specified format."""
    pipeline = AnalysisPipeline()
    return await pipeline.analyze_and_export(repo_path, format_type)
