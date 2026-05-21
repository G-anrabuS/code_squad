"""
Report Generator - Creates final comprehensive analysis report.
"""
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class ComprehensiveReport(BaseModel):
    """Final comprehensive analysis report."""
    
    timestamp: str
    repository_info: Dict[str, Any]
    project_summary: Dict[str, Any]
    architecture_analysis: Dict[str, Any]
    code_quality_assessment: Dict[str, Any]
    performance_analysis: Dict[str, Any]
    security_assessment: Dict[str, Any]
    recommendations: Dict[str, Any]
    priority_actions: List[str]


class ReportGenerator:
    """Generates comprehensive final report from all agent findings."""
    
    def generate_report(self, agents_findings: Dict[str, Any], codebase_data: Dict[str, Any]) -> ComprehensiveReport:
        """Generate comprehensive final report."""
        
        report = ComprehensiveReport(
            timestamp=datetime.now().isoformat(),
            repository_info=self._format_repository_info(codebase_data),
            project_summary=self._format_project_summary(agents_findings),
            architecture_analysis=self._format_architecture(agents_findings),
            code_quality_assessment=self._format_code_quality(agents_findings),
            performance_analysis=self._format_performance(agents_findings),
            security_assessment=self._format_security(agents_findings),
            recommendations=self._format_recommendations(agents_findings),
            priority_actions=self._generate_priority_actions(agents_findings),
        )
        
        return report
    
    def _format_repository_info(self, codebase_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format repository information."""
        return {
            'total_files': codebase_data.get('total_files', 0),
            'total_lines': sum(len(content.split('\n')) for content in codebase_data.get('files', {}).values()) if codebase_data.get('files') else 0,
            'project_type': codebase_data.get('project_type', 'Unknown'),
            'tech_stack': codebase_data.get('tech_stack', []),
            'important_files': codebase_data.get('important_files', [])[:10],
            'file_structure': {
                'folders': codebase_data.get('file_tree', {}).get('children', [])[:10],
                'total_extensions': len(set(f.split('.')[-1] for f in codebase_data.get('important_files', []))),
            }
        }
    
    def _format_project_summary(self, agents_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Format project summary from summary agent."""
        summary_agent = agents_findings.get('summary', {})
        findings = summary_agent.get('findings', {})
        
        return {
            'overview': findings.get('project_overview', ''),
            'major_modules': findings.get('major_modules', []),
            'architecture_flow': findings.get('architecture_flow', ''),
            'technologies_used': findings.get('technologies_used', []),
            'integrations': findings.get('integrations', []),
            'backend_structure': findings.get('backend_structure', {}),
            'frontend_structure': findings.get('frontend_structure', {}),
            'execution_pipeline': findings.get('execution_pipeline', ''),
        }
    
    def _format_architecture(self, agents_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Format architecture analysis."""
        architect_agent = agents_findings.get('architect', {})
        findings = architect_agent.get('findings', {})
        
        return {
            'current_pattern': findings.get('current_architecture', {}).get('pattern', ''),
            'maturity': findings.get('current_architecture', {}).get('maturity', ''),
            'complexity': findings.get('current_architecture', {}).get('complexity', ''),
            'folder_structure_issues': findings.get('folder_structure_issues', []),
            'modularization_opportunities': findings.get('modularization_opportunities', []),
            'service_separation': findings.get('service_separation', []),
            'refactoring_opportunities': findings.get('refactoring_opportunities', []),
            'improved_architecture': findings.get('improved_architecture_proposal', {}),
        }
    
    def _format_code_quality(self, agents_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Format code quality assessment."""
        judge_agent = agents_findings.get('judge', {})
        findings = judge_agent.get('findings', {})
        
        return {
            'overall_score': findings.get('code_quality_score', 0),
            'maintainability': findings.get('maintainability', 0),
            'scalability': findings.get('scalability', 0),
            'readability': findings.get('readability', 0),
            'modularity': findings.get('modularity', 0),
            'design_consistency': findings.get('design_consistency', 0),
            'technical_debt': findings.get('technical_debt', []),
            'potential_bugs': findings.get('potential_bugs', []),
            'anti_patterns': findings.get('anti_patterns', []),
        }
    
    def _format_performance(self, agents_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Format performance analysis."""
        perf_agent = agents_findings.get('performance', {})
        findings = perf_agent.get('findings', {})
        
        return {
            'bottlenecks': findings.get('bottlenecks', []),
            'inefficient_patterns': findings.get('inefficient_patterns', []),
            'memory_issues': findings.get('memory_issues', []),
            'async_handling_score': findings.get('async_handling', {}).get('score', 0),
            'caching_opportunities': findings.get('caching_opportunities', []),
            'database_issues': findings.get('database_issues', []),
            'optimization_strategies': findings.get('optimization_strategies', []),
            'priority_fixes': findings.get('priority_fixes', []),
        }
    
    def _format_security(self, agents_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Format security assessment."""
        security_agent = agents_findings.get('security', {})
        findings = security_agent.get('findings', {})
        severity = security_agent.get('severity', 'MEDIUM')
        
        return {
            'severity_level': severity,
            'critical_vulnerabilities': findings.get('critical_vulnerabilities', []),
            'high_risk_issues': findings.get('high_risk_issues', []),
            'medium_risk_issues': findings.get('medium_risk_issues', []),
            'dependency_risks': findings.get('dependency_risks', []),
            'authentication_mechanisms': findings.get('authentication_issues', []),
            'api_security_score': findings.get('api_security', {}).get('score', 0),
            'data_handling_issues': findings.get('data_handling', {}).get('issues', []),
            'compliance_risks': findings.get('compliance_risks', []),
        }
    
    def _format_recommendations(self, agents_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Format all recommendations."""
        return {
            'codebase_organization': agents_findings.get('codebase_analyzer', {}).get('recommendations', []),
            'architecture_improvements': agents_findings.get('architect', {}).get('recommendations', []),
            'code_quality_fixes': agents_findings.get('judge', {}).get('recommendations', []),
            'performance_optimizations': agents_findings.get('performance', {}).get('recommendations', []),
            'security_fixes': agents_findings.get('security', {}).get('recommendations', []),
        }
    
    def _generate_priority_actions(self, agents_findings: Dict[str, Any]) -> List[str]:
        """Generate priority action list."""
        actions = []
        
        # Security first
        security = agents_findings.get('security', {}).get('findings', {})
        if security.get('critical_vulnerabilities'):
            actions.append(f"🔴 CRITICAL: Fix {security['critical_vulnerabilities'][0]}")
        
        if security.get('high_risk_issues'):
            actions.append(f"🔴 HIGH: {security['high_risk_issues'][0]}")
        
        # Performance
        perf = agents_findings.get('performance', {}).get('findings', {})
        if perf.get('priority_fixes'):
            fix = perf['priority_fixes'][0]
            actions.append(f"🟠 PERFORMANCE: {fix[0]}")
        
        # Architecture
        arch = agents_findings.get('architect', {}).get('findings', {})
        if arch.get('refactoring_opportunities'):
            actions.append(f"🟡 REFACTOR: {arch['refactoring_opportunities'][0]}")
        
        # Code Quality
        judge = agents_findings.get('judge', {}).get('findings', {})
        if judge.get('technical_debt'):
            actions.append(f"🟡 TECHNICAL DEBT: {judge['technical_debt'][0]}")
        
        return actions[:10]  # Top 10 priority actions
    
    def to_dict(self, report: ComprehensiveReport) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return report.dict()
    
    def to_markdown(self, report: ComprehensiveReport) -> str:
        """Convert report to markdown format."""
        md = f"""
# Comprehensive Codebase Analysis Report

**Generated:** {report.timestamp}

---

## 📊 Repository Overview

- **Total Files:** {report.repository_info['total_files']}
- **Project Type:** {report.repository_info['project_type']}
- **Tech Stack:** {', '.join(report.repository_info['tech_stack'])}

### Important Files
{chr(10).join(f'- {f}' for f in report.repository_info['important_files'][:5])}

---

## 📖 Project Summary

{report.project_summary['overview']}

### Major Modules
{chr(10).join(f'- {m}' for m in report.project_summary['major_modules'])}

### Architecture Flow
{report.project_summary['architecture_flow']}

---

## 🏗️  Architecture Analysis

- **Current Pattern:** {report.architecture_analysis['current_pattern']}
- **Maturity Level:** {report.architecture_analysis['maturity']}
- **Complexity:** {report.architecture_analysis['complexity']}

### Issues Found
{chr(10).join(f'- {i}' for i in report.architecture_analysis['folder_structure_issues'][:3])}

### Refactoring Opportunities
{chr(10).join(f'- {o}' for o in report.architecture_analysis['refactoring_opportunities'][:3])}

---

## 💻 Code Quality Assessment

| Metric | Score |
|--------|-------|
| Overall Score | {report.code_quality_assessment['overall_score']:.0%} |
| Maintainability | {report.code_quality_assessment['maintainability']:.0%} |
| Scalability | {report.code_quality_assessment['scalability']:.0%} |
| Readability | {report.code_quality_assessment['readability']:.0%} |

### Technical Debt
{chr(10).join(f'- {d}' for d in report.code_quality_assessment['technical_debt'][:3])}

---

## ⚡ Performance Analysis

### Bottlenecks
{chr(10).join(f'- {b}' for b in report.performance_analysis['bottlenecks'][:3])}

### Optimization Strategies
{chr(10).join(f'- {s}' for s in report.performance_analysis['optimization_strategies'][:3])}

---

## 🔒 Security Assessment

**Severity Level:** {report.security_assessment['severity_level']}

### Critical Issues
{chr(10).join(f'- {v}' for v in report.security_assessment['critical_vulnerabilities'])}

### High Risk Issues
{chr(10).join(f'- {h}' for h in report.security_assessment['high_risk_issues'][:3])}

---

## 🎯 Priority Actions

{chr(10).join(f'{i+1}. {action}' for i, action in enumerate(report.priority_actions))}

---

## 📋 Recommendations Summary

### Architecture Improvements
{chr(10).join(f'- {r}' for r in report.recommendations['architecture_improvements'][:3])}

### Performance Optimizations
{chr(10).join(f'- {r}' for r in report.recommendations['performance_optimizations'][:3])}

### Security Enhancements
{chr(10).join(f'- {r}' for r in report.recommendations['security_fixes'][:3])}

---

**End of Report**
"""
        return md
