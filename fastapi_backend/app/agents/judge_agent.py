"""
Judge Agent - Reviews code quality, maintainability, and architectural decisions.
"""
from typing import Dict, Any, List
from app.agents.base_agent import BaseAnalysisAgent, AgentResponse
import re


class JudgeAgent(BaseAnalysisAgent):
    """Critically evaluates code quality and architecture."""
    
    def __init__(self):
        super().__init__("Judge Agent")
        
    async def analyze(self, codebase_data: Dict[str, Any]) -> AgentResponse:
        """Evaluate codebase quality."""
        
        findings = {
            'code_quality_score': self._assess_code_quality(codebase_data),
            'maintainability': self._assess_maintainability(codebase_data),
            'scalability': self._assess_scalability(codebase_data),
            'readability': self._assess_readability(codebase_data),
            'modularity': self._assess_modularity(codebase_data),
            'design_consistency': self._assess_design_consistency(codebase_data),
            'technical_debt': self._identify_technical_debt(codebase_data),
            'potential_bugs': self._identify_potential_bugs(codebase_data),
            'anti_patterns': self._identify_anti_patterns(codebase_data),
        }
        
        overall_quality = (
            findings['code_quality_score'] +
            findings['maintainability'] +
            findings['scalability'] +
            findings['readability']
        ) / 4
        
        summary = f"""
        CODE QUALITY ASSESSMENT:
        
        Overall Quality Score: {overall_quality:.1%}
        - Maintainability: {findings['maintainability']:.1%}
        - Scalability: {findings['scalability']:.1%}
        - Readability: {findings['readability']:.1%}
        - Modularity: {findings['modularity']:.1%}
        
        Technical Debt Issues: {len(findings['technical_debt'])}
        Potential Bugs Found: {len(findings['potential_bugs'])}
        Anti-patterns Detected: {len(findings['anti_patterns'])}
        """
        
        recommendations = self._generate_criticisms(findings)
        
        return self.format_findings(findings, summary.strip(), recommendations)
    
    def _assess_code_quality(self, codebase_data: Dict[str, Any]) -> float:
        """Assess overall code quality."""
        score = 0.7  # Base score
        
        total_files = codebase_data.get('total_files', 0)
        if total_files < 50:
            score += 0.15
        
        tech_stack = codebase_data.get('tech_stack', [])
        modern_techs = ['TypeScript', 'Python', 'Go']
        if any(t in tech_stack for t in modern_techs):
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_maintainability(self, codebase_data: Dict[str, Any]) -> float:
        """Assess code maintainability."""
        score = 0.6
        
        file_org = codebase_data.get('file_tree', {})
        if file_org:
            score += 0.2
        
        # Check for documentation indicators
        important_files = codebase_data.get('important_files', [])
        has_readme = any('readme' in f.lower() for f in important_files)
        if has_readme:
            score += 0.15
        
        return min(score, 1.0)
    
    def _assess_scalability(self, codebase_data: Dict[str, Any]) -> float:
        """Assess codebase scalability."""
        score = 0.5
        
        tech_stack = codebase_data.get('tech_stack', [])
        scalable_techs = ['FastAPI', 'Spring', 'Go', 'Kubernetes', 'Docker']
        if any(t in tech_stack for t in scalable_techs):
            score += 0.3
        
        total_files = codebase_data.get('total_files', 0)
        if total_files > 100:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_readability(self, codebase_data: Dict[str, Any]) -> float:
        """Assess code readability."""
        score = 0.65
        
        # Python files tend to be more readable
        tech_stack = codebase_data.get('tech_stack', [])
        if 'Python' in tech_stack:
            score += 0.15
        
        return min(score, 1.0)
    
    def _assess_modularity(self, codebase_data: Dict[str, Any]) -> float:
        """Assess code modularity."""
        score = 0.5
        
        important_files = codebase_data.get('important_files', [])
        
        # Check for modular structure
        module_indicators = ['models', 'services', 'controllers', 'api', 'utils', 'core']
        modular_count = sum(1 for f in important_files if any(m in f.lower() for m in module_indicators))
        
        if modular_count > 3:
            score += 0.3
        elif modular_count > 0:
            score += 0.15
        
        return min(score, 1.0)
    
    def _assess_design_consistency(self, codebase_data: Dict[str, Any]) -> float:
        """Assess design pattern consistency."""
        score = 0.6
        
        important_files = codebase_data.get('important_files', [])
        
        # Look for consistent patterns
        patterns = ['model', 'service', 'controller', 'repository', 'factory']
        pattern_count = len(set(p for f in important_files for p in patterns if p in f.lower()))
        
        if pattern_count >= 3:
            score += 0.25
        
        return min(score, 1.0)
    
    def _identify_technical_debt(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Identify technical debt."""
        debt_items = []
        
        total_files = codebase_data.get('total_files', 0)
        if total_files > 200:
            debt_items.append("Large codebase without modularization")
        
        important_files = codebase_data.get('important_files', [])
        if not any('test' in f.lower() for f in important_files):
            debt_items.append("Missing test files - testing infrastructure needed")
        
        if not any('doc' in f.lower() or 'readme' in f.lower() for f in important_files):
            debt_items.append("Insufficient documentation")
        
        dependencies = codebase_data.get('dependencies', {})
        all_deps = []
        for dep_list in dependencies.values():
            all_deps.extend(dep_list)
        
        if len(all_deps) > 50:
            debt_items.append("High number of dependencies - consider consolidation")
        
        return debt_items
    
    def _identify_potential_bugs(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Identify potential bugs and issues."""
        bugs = []
        
        # Common bug patterns
        important_files = codebase_data.get('important_files', [])
        
        if not any('error' in f.lower() or 'exception' in f.lower() for f in important_files):
            bugs.append("Missing centralized error handling")
        
        if not any('logging' in f.lower() or 'logger' in f.lower() for f in important_files):
            bugs.append("Missing logging infrastructure")
        
        if not any('validation' in f.lower() or 'validator' in f.lower() for f in important_files):
            bugs.append("No input validation detected")
        
        return bugs
    
    def _identify_anti_patterns(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Identify anti-patterns and bad practices."""
        anti_patterns = []
        
        total_files = codebase_data.get('total_files', 0)
        important_files = codebase_data.get('important_files', [])
        
        # Check for god objects
        if total_files < 10 and important_files:
            anti_patterns.append("Possible god object pattern - consider splitting main files")
        
        # Check for configuration management
        if not any('config' in f.lower() for f in important_files):
            anti_patterns.append("Hardcoded configuration - use config management")
        
        # Check for secrets
        if any('secret' in f.lower() or 'key' in f.lower() for f in important_files):
            # Check if it's a key file or just contains references
            if not any('config' in f.lower() for f in important_files):
                anti_patterns.append("Possible hardcoded secrets - use environment variables")
        
        return anti_patterns
    
    def _generate_criticisms(self, findings: Dict[str, Any]) -> List[str]:
        """Generate critical feedback."""
        criticisms = []
        
        if findings['code_quality_score'] < 0.6:
            criticisms.append("Code quality needs significant improvement")
        
        if findings['maintainability'] < 0.5:
            criticisms.append("Code structure makes maintenance difficult")
        
        if findings['scalability'] < 0.5:
            criticisms.append("Current architecture won't scale well")
        
        if findings['technical_debt']:
            criticisms.append(f"Address technical debt: {findings['technical_debt'][0]}")
        
        if findings['anti_patterns']:
            criticisms.append(f"Fix anti-patterns: {findings['anti_patterns'][0]}")
        
        if not criticisms:
            criticisms.append("Code quality is acceptable - focus on scalability")
        
        return criticisms
