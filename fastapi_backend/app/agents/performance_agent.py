"""
Performance Agent - Detects performance bottlenecks and optimization opportunities.
"""
from typing import Dict, Any, List, Tuple
from app.agents.base_agent import BaseAnalysisAgent, AgentResponse


class PerformanceAgent(BaseAnalysisAgent):
    """Detects performance issues and suggests optimizations."""
    
    def __init__(self):
        super().__init__("Performance Agent")
        
    async def analyze(self, codebase_data: Dict[str, Any]) -> AgentResponse:
        """Analyze performance bottlenecks."""
        
        findings = {
            'bottlenecks': self._identify_bottlenecks(codebase_data),
            'inefficient_patterns': self._find_inefficient_patterns(codebase_data),
            'memory_issues': self._identify_memory_issues(codebase_data),
            'async_handling': self._assess_async_handling(codebase_data),
            'caching_opportunities': self._identify_caching_opportunities(codebase_data),
            'database_issues': self._identify_database_issues(codebase_data),
            'optimization_strategies': self._generate_optimization_strategies(codebase_data),
            'priority_fixes': self._prioritize_fixes(codebase_data),
        }
        
        summary = f"""
        PERFORMANCE ANALYSIS:
        
        Critical Bottlenecks: {len(findings['bottlenecks'])}
        Inefficient Patterns Found: {len(findings['inefficient_patterns'])}
        Memory Issues: {len(findings['memory_issues'])}
        Caching Opportunities: {len(findings['caching_opportunities'])}
        
        Priority Fixes:
        {chr(10).join(f"- {fix[0]} (Impact: {fix[1]})" for fix in findings['priority_fixes'][:3])}
        
        Recommendation: {findings['optimization_strategies'][0] if findings['optimization_strategies'] else 'Review async patterns'}
        """
        
        recommendations = self._generate_performance_recommendations(findings)
        
        return self.format_findings(
            findings, 
            summary.strip(), 
            recommendations,
            severity='HIGH' if len(findings['bottlenecks']) > 2 else 'MEDIUM'
        )
    
    def _identify_bottlenecks(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Identify performance bottlenecks."""
        bottlenecks = []
        
        tech_stack = codebase_data.get('tech_stack', [])
        
        # API bottleneck patterns
        if 'FastAPI' in tech_stack or 'Django' in tech_stack:
            bottlenecks.append("Potential N+1 database queries in list endpoints")
            bottlenecks.append("Missing database query optimization (indexes, pagination)")
        
        if 'React' in tech_stack or 'Vue' in tech_stack:
            bottlenecks.append("Potential unnecessary re-renders on state changes")
            bottlenecks.append("Large bundle size from unoptimized dependencies")
        
        total_files = codebase_data.get('total_files', 0)
        if total_files > 100:
            bottlenecks.append("Large codebase may have slow build times")
        
        dependencies = codebase_data.get('dependencies', {})
        all_deps = []
        for dep_list in dependencies.values():
            all_deps.extend(dep_list)
        
        if len(all_deps) > 30:
            bottlenecks.append("High dependency count may slow package installation")
        
        return bottlenecks
    
    def _find_inefficient_patterns(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Find inefficient coding patterns."""
        patterns = []
        
        important_files = codebase_data.get('important_files', [])
        
        # Check for common anti-patterns
        if any('util' in f.lower() for f in important_files):
            patterns.append("Utility functions may be called frequently - consider memoization")
        
        if any('loop' in f.lower() or 'batch' in f.lower() for f in important_files):
            patterns.append("Batch processing loops detected - verify efficiency")
        
        if any('data' in f.lower() or 'cache' in f.lower() for f in important_files):
            patterns.append("Data processing logic - ensure streaming when possible")
        
        if not any('async' in f.lower() or 'background' in f.lower() for f in important_files):
            patterns.append("Missing async task handling for long-running operations")
        
        return patterns
    
    def _identify_memory_issues(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Identify memory-related issues."""
        issues = []
        
        tech_stack = codebase_data.get('tech_stack', [])
        
        # Memory issues for specific stacks
        if 'React' in tech_stack:
            issues.append("Memory leaks from uncleared subscriptions/listeners")
            issues.append("Large state objects causing memory growth")
        
        if 'Python' in tech_stack or 'FastAPI' in tech_stack:
            issues.append("Unbounded list/dict growth without cleanup")
            issues.append("Circular references preventing garbage collection")
        
        total_files = codebase_data.get('total_files', 0)
        if total_files > 200:
            issues.append("Large module loading times from importing everything")
        
        return issues
    
    def _assess_async_handling(self, codebase_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess async/await patterns."""
        important_files = codebase_data.get('important_files', [])
        
        has_async = any('async' in f.lower() for f in important_files)
        has_background_jobs = any('background' in f.lower() or 'task' in f.lower() or 'celery' in f.lower() for f in important_files)
        has_promises = any('promise' in f.lower() or 'then' in f.lower() for f in important_files)
        
        return {
            'has_async_code': has_async,
            'has_background_jobs': has_background_jobs,
            'has_promise_handling': has_promises,
            'score': (int(has_async) + int(has_background_jobs) + int(has_promises)) / 3
        }
    
    def _identify_caching_opportunities(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Identify caching opportunities."""
        opportunities = []
        
        tech_stack = codebase_data.get('tech_stack', [])
        
        if 'Redis' not in tech_stack:
            opportunities.append("Implement Redis for session/data caching")
        
        if 'FastAPI' in tech_stack or 'Django' in tech_stack:
            opportunities.append("Cache expensive database queries")
            opportunities.append("Implement HTTP caching headers")
            opportunities.append("Cache external API responses")
        
        if 'React' in tech_stack or 'Vue' in tech_stack:
            opportunities.append("Implement client-side caching for API responses")
            opportunities.append("Use React Query or SWR for smart caching")
        
        important_files = codebase_data.get('important_files', [])
        if not any('cache' in f.lower() for f in important_files):
            opportunities.append("No caching infrastructure detected")
        
        return opportunities
    
    def _identify_database_issues(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Identify database performance issues."""
        issues = []
        
        important_files = codebase_data.get('important_files', [])
        
        if any('database' in f.lower() or 'db' in f.lower() for f in important_files):
            issues.append("Verify all critical queries have proper indexes")
            issues.append("Check for missing connection pooling")
            issues.append("Audit for N+1 query problems")
            issues.append("Review query complexity and execution plans")
        
        if not any('migration' in f.lower() for f in important_files):
            issues.append("No migration system detected - risk of schema drift")
        
        return issues
    
    def _generate_optimization_strategies(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Generate optimization strategies."""
        strategies = []
        
        tech_stack = codebase_data.get('tech_stack', [])
        
        if 'FastAPI' in tech_stack or 'Django' in tech_stack:
            strategies.append("Profile database queries using tools like django-debug-toolbar or fastapi debugging")
            strategies.append("Implement pagination for list endpoints")
            strategies.append("Use connection pooling for database connections")
        
        if 'React' in tech_stack or 'Vue' in tech_stack:
            strategies.append("Code splitting and lazy loading for routes")
            strategies.append("Image optimization and compression")
            strategies.append("Minification and bundling optimization")
        
        if 'Python' in tech_stack:
            strategies.append("Use PyPy or Cython for CPU-intensive operations")
            strategies.append("Implement request queuing for burst traffic")
        
        strategies.append("Set up monitoring and alerting for performance metrics")
        
        return strategies
    
    def _prioritize_fixes(self, codebase_data: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Prioritize fixes by impact."""
        fixes = []
        
        bottlenecks = self._identify_bottlenecks(codebase_data)
        caching = self._identify_caching_opportunities(codebase_data)
        db_issues = self._identify_database_issues(codebase_data)
        
        # High impact fixes
        for issue in db_issues[:2]:
            fixes.append((issue, "HIGH"))
        
        for issue in caching[:2]:
            fixes.append((issue, "HIGH"))
        
        for issue in bottlenecks[:1]:
            fixes.append((issue, "MEDIUM"))
        
        return fixes
    
    def _generate_performance_recommendations(self, findings: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        if len(findings['bottlenecks']) > 0:
            recommendations.append(f"Critical: Fix {findings['bottlenecks'][0]}")
        
        if findings['async_handling']['score'] < 0.5:
            recommendations.append("Implement async/await patterns for I/O operations")
        
        if findings['caching_opportunities']:
            recommendations.append(f"Add caching: {findings['caching_opportunities'][0]}")
        
        if findings['priority_fixes']:
            recommendations.append(f"Priority 1: {findings['priority_fixes'][0][0]}")
        
        return recommendations
