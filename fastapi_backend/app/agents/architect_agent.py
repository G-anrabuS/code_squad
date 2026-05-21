"""
Architect Agent - Analyzes and suggests improved architecture and refactoring.
"""

from typing import Dict, Any, List
from app.agents.base_agent import BaseAnalysisAgent, AgentResponse


class ArchitectAgent(BaseAnalysisAgent):
    """Analyzes architecture and suggests improvements."""

    def __init__(self):
        super().__init__("Architect Agent")

    async def analyze(self, codebase_data: Dict[str, Any]) -> AgentResponse:
        """Analyze and suggest architecture improvements."""

        findings = {
            "current_architecture": self._analyze_current_architecture(codebase_data),
            "folder_structure_issues": self._analyze_folder_structure(codebase_data),
            "modularization_opportunities": self._identify_modularization_opportunities(
                codebase_data
            ),
            "service_separation": self._suggest_service_separation(codebase_data),
            "scalability_improvements": self._suggest_scalability_improvements(
                codebase_data
            ),
            "design_patterns": self._suggest_design_patterns(codebase_data),
            "refactoring_opportunities": self._identify_refactoring_opportunities(
                codebase_data
            ),
            "improved_architecture_proposal": self._propose_improved_architecture(
                codebase_data
            ),
        }

        summary = f"""
        ARCHITECTURE ANALYSIS:

        Current Pattern: {findings['current_architecture'].get('pattern', 'Mixed')}
        Maturity Level: {findings['current_architecture'].get('maturity', 'Growing')}

        Modularization Opportunities: {len(findings['modularization_opportunities'])}
        Refactoring Candidates: {len(findings['refactoring_opportunities'])}

        Recommended Design Patterns:
        {chr(10).join(f"- {p}" for p in findings['design_patterns'][:3])}

        Key Improvement Areas:
        {chr(10).join(f"- {imp}" for imp in findings['scalability_improvements'][:3])}
        """

        recommendations = self._generate_architecture_recommendations(findings)

        return self.format_findings(findings, summary.strip(), recommendations)

    def _analyze_current_architecture(
        self, codebase_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze current architecture pattern."""
        tech_stack = codebase_data.get("tech_stack", [])
        important_files = codebase_data.get("important_files", [])

        # Determine architecture pattern
        pattern = "Unknown"
        if any(t in tech_stack for t in ["FastAPI", "Django", "Spring"]):
            pattern = "REST API"
        elif any(t in tech_stack for t in ["React", "Vue", "Angular"]):
            pattern = "Frontend Application"

        if any("micro" in f.lower() or "service" in f.lower() for f in important_files):
            pattern = "Microservices"
        elif any("controller" in f.lower() for f in important_files):
            pattern = "MVC/MVT"

        return {
            "pattern": pattern,
            "maturity": self._assess_maturity(codebase_data),
            "complexity": self._assess_complexity(codebase_data),
        }

    def _assess_maturity(self, codebase_data: Dict[str, Any]) -> str:
        """Assess architecture maturity."""
        important_files = codebase_data.get("important_files", [])
        total_files = codebase_data.get("total_files", 0)

        if total_files < 20:
            return "Early Stage"
        elif total_files < 50 and len(important_files) > 5:
            return "Growing"
        elif total_files < 100:
            return "Established"
        else:
            return "Mature"

    def _assess_complexity(self, codebase_data: Dict[str, Any]) -> str:
        """Assess architecture complexity."""
        total_files = codebase_data.get("total_files", 0)
        dependencies = codebase_data.get("dependencies", {})

        dep_count = sum(len(v) for v in dependencies.values())

        if total_files < 30 or dep_count < 15:
            return "Simple"
        elif total_files < 100 or dep_count < 40:
            return "Moderate"
        else:
            return "Complex"

    def _analyze_folder_structure(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Analyze folder structure issues."""
        issues = []

        file_tree = codebase_data.get("file_tree", {})
        children = file_tree.get("children", [])

        # Check if structure is flat
        if len(children) < 3:
            issues.append("Flat folder structure - lack of logical grouping")

        # Check for well-known patterns
        has_models = any("model" in str(item).lower() for item in children)
        has_views = any("view" in str(item).lower() for item in children)
        has_controller = any("controller" in str(item).lower() for item in children)

        if not has_models:
            issues.append("No clear data model layer")

        if not any("service" in str(item).lower() for item in children):
            issues.append("Business logic not separated into services")

        if not any(
            "api" in str(item).lower() or "router" in str(item).lower()
            for item in children
        ):
            issues.append("No dedicated API/routing layer")

        if not issues:
            issues.append("Folder structure is well-organized")

        return issues

    def _identify_modularization_opportunities(
        self, codebase_data: Dict[str, Any]
    ) -> List[str]:
        """Identify opportunities for better modularization."""
        opportunities = []

        important_files = codebase_data.get("important_files", [])

        # Identify features that could be modules
        features = set()
        for file in important_files:
            if "auth" in file.lower():
                features.add("Authentication Module")
            if "payment" in file.lower() or "order" in file.lower():
                features.add("Payment Module")
            if "user" in file.lower():
                features.add("User Management Module")
            if "repo" in file.lower() or "github" in file.lower():
                features.add("Repository Integration Module")

        if len(features) > 0:
            opportunities.extend(list(features))

        if len(important_files) > 10:
            opportunities.append("Extract shared utilities into separate module")
            opportunities.append("Create middleware layer for cross-cutting concerns")

        return opportunities

    def _suggest_service_separation(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Suggest how to separate services."""
        suggestions = []

        tech_stack = codebase_data.get("tech_stack", [])

        if any(t in tech_stack for t in ["Python", "FastAPI", "Django"]):
            suggestions.append("Separate API routing from business logic")
            suggestions.append("Create service layer for database operations")
            suggestions.append("Extract authentication into dedicated service")

        if "React" in tech_stack:
            suggestions.append("Separate API client from UI components")
            suggestions.append("Create state management layer")

        return suggestions

    def _suggest_scalability_improvements(
        self, codebase_data: Dict[str, Any]
    ) -> List[str]:
        """Suggest scalability improvements."""
        improvements = []

        tech_stack = codebase_data.get("tech_stack", [])

        if "FastAPI" not in tech_stack and "Python" in tech_stack:
            improvements.append("Migrate to FastAPI for async support")

        if "Docker" not in tech_stack:
            improvements.append("Add Docker containerization")

        if "Kubernetes" not in tech_stack and codebase_data.get("total_files", 0) > 50:
            improvements.append("Prepare for Kubernetes orchestration")

        if "Redis" not in tech_stack:
            improvements.append("Add caching layer with Redis")

        if not any("queue" in t.lower() or "celery" in t.lower() for t in tech_stack):
            improvements.append("Implement job queue for async tasks")

        return improvements

    def _suggest_design_patterns(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Suggest applicable design patterns."""
        patterns = [
            "Repository Pattern for data access",
            "Service Locator Pattern for dependency management",
            "Factory Pattern for object creation",
            "Observer Pattern for event handling",
            "Strategy Pattern for algorithm selection",
            "Builder Pattern for complex object construction",
            "Singleton Pattern for shared resources",
            "Decorator Pattern for feature enhancement",
        ]

        return patterns

    def _identify_refactoring_opportunities(
        self, codebase_data: Dict[str, Any]
    ) -> List[str]:
        """Identify specific refactoring opportunities."""
        opportunities = []

        important_files = codebase_data.get("important_files", [])
        total_files = codebase_data.get("total_files", 0)

        if total_files > 50:
            opportunities.append("Break down large monolithic files")

        if any("main" in f.lower() for f in important_files):
            opportunities.append("Extract bootstrap logic from main")

        if any("util" in f.lower() for f in important_files):
            opportunities.append("Organize utilities into feature-specific modules")

        if any("config" in f.lower() for f in important_files):
            opportunities.append("Implement configuration hierarchy")

        return opportunities

    def _propose_improved_architecture(
        self, codebase_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Propose improved architecture."""
        current = self._analyze_current_architecture(codebase_data)

        proposal = {
            "pattern": current["pattern"],
            "recommended_layers": [
                "API Layer (Controllers/Routers)",
                "Service Layer (Business Logic)",
                "Repository Layer (Data Access)",
                "Models Layer (Data Structures)",
                "Middleware Layer (Cross-cutting Concerns)",
                "Config & Utils",
            ],
            "module_structure": self._propose_module_structure(codebase_data),
            "technology_recommendations": self._recommend_technologies(codebase_data),
        }

        return proposal

    def _propose_module_structure(
        self, codebase_data: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Propose module structure."""
        return {
            "core": [
                "config/",
                "constants/",
                "exceptions/",
            ],
            "features": [
                "authentication/",
                "users/",
                "repositories/",
                "analysis/",
            ],
            "shared": [
                "services/",
                "models/",
                "utils/",
                "middleware/",
            ],
            "tests": [
                "unit/",
                "integration/",
                "e2e/",
            ],
        }

    def _recommend_technologies(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Recommend additional technologies."""
        tech_stack = codebase_data.get("tech_stack", [])
        recommendations = []

        if "Python" in tech_stack and "FastAPI" not in tech_stack:
            recommendations.append("FastAPI for async web framework")

        if "Docker" not in tech_stack:
            recommendations.append("Docker for containerization")

        if not any("pytest" in str(t).lower() for t in tech_stack):
            recommendations.append("pytest for testing")

        if "PostgreSQL" not in tech_stack:
            recommendations.append("PostgreSQL for production database")

        return recommendations

    def _generate_architecture_recommendations(
        self, findings: Dict[str, Any]
    ) -> List[str]:
        """Generate architecture recommendations."""
        recommendations = []

        current = findings["current_architecture"]
        if current["complexity"] == "Complex":
            recommendations.append(
                "Your architecture is complex - ensure proper documentation"
            )

        if findings["folder_structure_issues"]:
            recommendations.append(
                f"Restructure folders: {findings['folder_structure_issues'][0]}"
            )

        if findings["modularization_opportunities"]:
            recommendations.append(
                f"Create modules for: {findings['modularization_opportunities'][0]}"
            )

        if findings["scalability_improvements"]:
            recommendations.append(
                f"For scalability: {findings['scalability_improvements'][0]}"
            )

        return recommendations
