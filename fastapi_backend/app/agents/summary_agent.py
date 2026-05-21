"""
Summary Agent - Generates comprehensive project overview.
"""
from typing import Dict, Any, List
from app.agents.base_agent import BaseAnalysisAgent, AgentResponse


class SummaryAgent(BaseAnalysisAgent):
    """Generates comprehensive project summary and documentation."""
    
    def __init__(self):
        super().__init__("Summary Agent")
        
    async def analyze(self, codebase_data: Dict[str, Any]) -> AgentResponse:
        """Generate comprehensive project summary."""
        
        findings = {
            'project_overview': self._generate_overview(codebase_data),
            'major_modules': self._identify_major_modules(codebase_data),
            'architecture_flow': self._describe_architecture(codebase_data),
            'technologies_used': codebase_data.get('tech_stack', []),
            'integrations': self._identify_integrations(codebase_data),
            'backend_structure': self._analyze_backend(codebase_data),
            'frontend_structure': self._analyze_frontend(codebase_data),
            'execution_pipeline': self._analyze_execution_flow(codebase_data),
        }
        
        summary = f"""
        PROJECT SUMMARY:
        
        Type: {codebase_data.get('project_type', 'Unknown')}
        Tech Stack: {', '.join(findings['technologies_used'])}
        Major Modules: {len(findings['major_modules'])} identified
        
        Overview:
        {findings['project_overview']}
        
        Key Integration Points: {len(findings['integrations'])}
        """
        
        recommendations = [
            f"Focus on {findings['major_modules'][0] if findings['major_modules'] else 'core'} module for refactoring",
            f"Current architecture is {self._assess_complexity(codebase_data)} complexity",
            "Ensure all modules have documentation"
        ]
        
        return self.format_findings(findings, summary.strip(), recommendations)
    
    def _generate_overview(self, codebase_data: Dict[str, Any]) -> str:
        """Generate project overview description."""
        project_type = codebase_data.get('project_type', 'General')
        total_files = codebase_data.get('total_files', 0)
        tech_stack = codebase_data.get('tech_stack', [])
        
        overview = f"This is a {project_type} project built with {', '.join(tech_stack[:3])}. "
        overview += f"The codebase contains {total_files} code files organized into logical modules. "
        
        if any(t in tech_stack for t in ['Python', 'FastAPI', 'Django', 'Flask']):
            overview += "It includes backend API services. "
        
        if any(t in tech_stack for t in ['JavaScript', 'TypeScript', 'React', 'Vue', 'Angular']):
            overview += "It includes frontend user interfaces. "
        
        return overview
    
    def _identify_major_modules(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Identify major project modules."""
        modules = set()
        important_files = codebase_data.get('important_files', [])
        
        module_keywords = {
            'api': 'API Module',
            'auth': 'Authentication',
            'service': 'Services',
            'models': 'Data Models',
            'database': 'Database Layer',
            'config': 'Configuration',
            'middleware': 'Middleware',
            'utils': 'Utilities',
            'core': 'Core Functionality'
        }
        
        for file_path in important_files:
            for keyword, module_name in module_keywords.items():
                if keyword in file_path.lower() and module_name not in modules:
                    modules.add(module_name)
        
        return list(modules)
    
    def _describe_architecture(self, codebase_data: Dict[str, Any]) -> str:
        """Describe the project architecture flow."""
        major_modules = self._identify_major_modules(codebase_data)
        
        if not major_modules:
            return "Standard layered architecture with application logic"
        
        flow = " → ".join(major_modules[:5])
        return f"Typical flow: {flow}"
    
    def _identify_integrations(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Identify external integrations."""
        integrations = []
        dependencies = codebase_data.get('dependencies', {})
        
        integration_map = {
            'boto3': 'AWS',
            'google': 'Google Cloud',
            'stripe': 'Stripe Payment',
            'twilio': 'Twilio SMS',
            'firebase': 'Firebase',
            'postgresql': 'PostgreSQL',
            'mongodb': 'MongoDB',
            'redis': 'Redis Cache',
            'elasticsearch': 'Elasticsearch',
        }
        
        all_deps = []
        for dep_list in dependencies.values():
            all_deps.extend(dep_list)
        
        for dep, integration in integration_map.items():
            if any(dep.lower() in d.lower() for d in all_deps):
                integrations.append(integration)
        
        return integrations
    
    def _analyze_backend(self, codebase_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze backend structure."""
        tech_stack = codebase_data.get('tech_stack', [])
        has_backend = any(t in tech_stack for t in ['Python', 'Java', 'Go', 'Node.js'])
        
        return {
            'exists': has_backend,
            'technologies': [t for t in tech_stack if t in ['Python', 'FastAPI', 'Django', 'Java', 'Spring']],
            'api_framework': next((t for t in tech_stack if 'API' in t or 'FastAPI' in t or 'Django' in t), None)
        }
    
    def _analyze_frontend(self, codebase_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze frontend structure."""
        tech_stack = codebase_data.get('tech_stack', [])
        has_frontend = any(t in tech_stack for t in ['JavaScript', 'TypeScript', 'React', 'Vue', 'Angular'])
        
        return {
            'exists': has_frontend,
            'frameworks': [t for t in tech_stack if t in ['React', 'Vue', 'Angular', 'Next.js']],
        }
    
    def _analyze_execution_flow(self, codebase_data: Dict[str, Any]) -> str:
        """Analyze typical execution flow."""
        project_type = codebase_data.get('project_type', '')
        
        if 'API' in project_type:
            return "HTTP Request → Router → Service → Database → Response"
        elif 'Frontend' in project_type:
            return "User Action → Component → State → API Call → Render"
        else:
            return "Input → Processing → Output"
    
    def _assess_complexity(self, codebase_data: Dict[str, Any]) -> str:
        """Assess overall project complexity."""
        total_files = codebase_data.get('total_files', 0)
        
        if total_files < 20:
            return "Low"
        elif total_files < 50:
            return "Low-Medium"
        elif total_files < 100:
            return "Medium"
        elif total_files < 200:
            return "Medium-High"
        else:
            return "High"
