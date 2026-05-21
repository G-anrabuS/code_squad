"""
Codebase Reader/Analyzer Agent - Traverses and understands repository structure.
"""
from typing import Dict, Any, List
from app.agents.base_agent import BaseAnalysisAgent, AgentResponse
from app.services.codebase_parser import CodebaseParser
import os


class CodebaseAnalyzerAgent(BaseAnalysisAgent):
    """Analyzes codebase structure, organization, and technology stack."""
    
    def __init__(self):
        super().__init__("Codebase Analyzer")
        
    async def analyze(self, codebase_data: Dict[str, Any]) -> AgentResponse:
        """Analyze codebase structure and content."""
        
        findings = {
            'repository_structure': codebase_data.get('file_tree', {}),
            'total_files': codebase_data.get('total_files', 0),
            'important_files': codebase_data.get('important_files', []),
            'tech_stack': codebase_data.get('tech_stack', []),
            'project_type': codebase_data.get('project_type', 'Unknown'),
            'dependencies': codebase_data.get('dependencies', {}),
            'file_organization': self._analyze_file_organization(codebase_data),
        }
        
        summary = f"""
        Repository Analysis Complete:
        - Total Files: {findings['total_files']}
        - Project Type: {findings['project_type']}
        - Technology Stack: {', '.join(findings['tech_stack'])}
        - Key Dependencies: {self._count_dependencies(findings['dependencies'])} packages
        - Organization: {findings['file_organization'].get('structure_type', 'Mixed')}
        """
        
        recommendations = self._generate_recommendations(findings)
        
        return self.format_findings(findings, summary.strip(), recommendations)
    
    def _analyze_file_organization(self, codebase_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how files are organized."""
        important_files = codebase_data.get('important_files', [])
        
        has_modular_structure = self._check_modular_structure(important_files)
        has_config_separation = self._check_config_separation(important_files)
        has_test_separation = self._check_test_separation(important_files)
        
        organization_score = sum([has_modular_structure, has_config_separation, has_test_separation]) / 3
        
        return {
            'structure_type': 'Well-Organized' if organization_score > 0.6 else 'Needs Organization',
            'organization_score': organization_score,
            'has_modular_structure': has_modular_structure,
            'has_config_separation': has_config_separation,
            'has_test_separation': has_test_separation,
        }
    
    def _check_modular_structure(self, files: List[str]) -> bool:
        """Check if codebase has modular directory structure."""
        modules = set()
        for file in files:
            parts = file.split(os.sep)
            if len(parts) > 1:
                modules.add(parts[0])
        return len(modules) > 3
    
    def _check_config_separation(self, files: List[str]) -> bool:
        """Check if configs are separated."""
        config_patterns = ['config', 'settings', 'env', '.yaml', '.yml', '.json']
        return any(any(pattern in f.lower() for pattern in config_patterns) for f in files)
    
    def _check_test_separation(self, files: List[str]) -> bool:
        """Check if tests are in separate location."""
        test_patterns = ['test', 'tests', 'spec', '__test__']
        return any(any(pattern in f.lower() for pattern in test_patterns) for f in files)
    
    def _count_dependencies(self, deps: Dict[str, List[str]]) -> int:
        """Count total dependencies."""
        return sum(len(v) for v in deps.values())
    
    def _generate_recommendations(self, findings: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if not findings['file_organization']['has_modular_structure']:
            recommendations.append("Consider implementing a modular directory structure for better organization")
        
        if not findings['file_organization']['has_config_separation']:
            recommendations.append("Separate configuration files from application code")
        
        if not findings['file_organization']['has_test_separation']:
            recommendations.append("Move tests to a dedicated test directory")
        
        if findings['total_files'] > 100:
            recommendations.append("Codebase is growing - ensure proper documentation exists")
        
        return recommendations
