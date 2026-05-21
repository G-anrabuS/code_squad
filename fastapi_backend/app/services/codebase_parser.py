"""
Codebase Parser - Traverses and analyzes repository structure.
"""
import os
import pathspec
from pathlib import Path
from typing import Dict, List, Set
import ast


class CodebaseParser:
    """Parse and analyze codebase structure."""
    
    # File extensions to include
    CODE_EXTENSIONS = {
        '.py', '.ts', '.tsx', '.js', '.jsx', '.java', '.cpp', '.c', '.go', '.rs',
        '.rb', '.php', '.swift', '.kt', '.scala', '.sh', '.sql', '.yaml', '.yml',
        '.json', '.toml', '.xml', '.html', '.css', '.scss'
    }
    
    # Directories to skip
    SKIP_DIRS = {
        '.git', '__pycache__', 'node_modules', '.next', 'build', 'dist', '.venv',
        'venv', '.env', '.pytest_cache', '.mypy_cache', '.idea', '.vscode',
        'target', 'bin', 'obj', '.gradle', '.maven', 'coverage', '.nyc_output'
    }
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.files: Dict[str, str] = {}
        self.structure: Dict = {}
        self.important_files: List[str] = []
        self.dependencies: Dict[str, List[str]] = {}
        self.file_tree: Dict = {}
        
    def parse(self) -> Dict:
        """Parse entire codebase."""
        self._build_file_tree()
        self._analyze_files()
        self._identify_important_files()
        self._extract_dependencies()
        
        return {
            'total_files': len(self.files),
            'file_tree': self.file_tree,
            'important_files': self.important_files,
            'dependencies': self.dependencies,
            'tech_stack': self._detect_tech_stack(),
            'project_type': self._detect_project_type(),
        }
    
    def _build_file_tree(self) -> None:
        """Recursively build file tree structure."""
        self.file_tree = {
            'name': self.repo_path.name,
            'path': str(self.repo_path),
            'type': 'directory',
            'children': self._traverse_directory(self.repo_path)
        }
    
    def _traverse_directory(self, path: Path, max_depth: int = 5, current_depth: int = 0) -> List[Dict]:
        """Traverse directory tree."""
        if current_depth >= max_depth:
            return []
        
        items = []
        try:
            for item in sorted(path.iterdir()):
                # Skip hidden and ignored directories
                if item.name.startswith('.') or item.name in self.SKIP_DIRS:
                    continue
                
                if item.is_dir():
                    children = self._traverse_directory(item, max_depth, current_depth + 1)
                    items.append({
                        'name': item.name,
                        'path': str(item.relative_to(self.repo_path)),
                        'type': 'directory',
                        'children': children,
                        'file_count': self._count_files(item)
                    })
                elif item.is_file() and item.suffix in self.CODE_EXTENSIONS:
                    items.append({
                        'name': item.name,
                        'path': str(item.relative_to(self.repo_path)),
                        'type': 'file',
                        'extension': item.suffix,
                        'size': item.stat().st_size
                    })
        except (PermissionError, OSError):
            pass
        
        return items
    
    def _count_files(self, path: Path) -> int:
        """Count code files in directory."""
        count = 0
        try:
            for item in path.rglob('*'):
                if item.is_file() and item.suffix in self.CODE_EXTENSIONS:
                    if not any(skip in item.parts for skip in self.SKIP_DIRS):
                        count += 1
        except (PermissionError, OSError):
            pass
        return count
    
    def _analyze_files(self) -> None:
        """Analyze all code files."""
        try:
            for root, dirs, files in os.walk(self.repo_path):
                # Remove skip directories
                dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS and not d.startswith('.')]
                
                for file in files:
                    if file.endswith(tuple(self.CODE_EXTENSIONS)):
                        file_path = Path(root) / file
                        try:
                            rel_path = str(file_path.relative_to(self.repo_path))
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                self.files[rel_path] = content
                        except (PermissionError, OSError):
                            pass
        except (PermissionError, OSError):
            pass
    
    def _identify_important_files(self) -> None:
        """Identify important/prioritized files."""
        important_patterns = [
            'main.py', 'app.py', 'index.ts', 'index.js', 'package.json',
            'requirements.txt', 'pom.xml', 'build.gradle', 'Dockerfile',
            'docker-compose.yml', 'settings.py', '.env.example', 'config.',
            'README', 'server.py', 'manage.py', 'api.py', 'models.py'
        ]
        
        for file_path in self.files.keys():
            filename = os.path.basename(file_path).lower()
            if any(pattern.lower() in filename for pattern in important_patterns):
                self.important_files.append(file_path)
        
        # Sort by importance
        self.important_files = sorted(
            self.important_files,
            key=lambda x: (os.path.basename(x).lower(), x)
        )[:20]  # Top 20 important files
    
    def _extract_dependencies(self) -> None:
        """Extract dependencies from config files."""
        # Check requirements.txt
        if 'requirements.txt' in self.files:
            self.dependencies['python'] = [
                line.split('==')[0] for line in self.files['requirements.txt'].split('\n')
                if line.strip() and not line.startswith('#')
            ]
        
        # Check package.json
        for path in self.files.keys():
            if 'package.json' in path:
                try:
                    import json
                    content = json.loads(self.files[path])
                    self.dependencies['npm'] = list(content.get('dependencies', {}).keys())
                    break
                except:
                    pass
        
        # Check pom.xml
        for path in self.files.keys():
            if 'pom.xml' in path:
                try:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(self.files[path])
                    deps = []
                    for dep in root.findall('.//{http://maven.apache.org/POM/4.0.0}dependency'):
                        artifact = dep.find('{http://maven.apache.org/POM/4.0.0}artifactId')
                        if artifact is not None:
                            deps.append(artifact.text)
                    if deps:
                        self.dependencies['maven'] = deps
                    break
                except:
                    pass
    
    def _detect_tech_stack(self) -> List[str]:
        """Detect technology stack."""
        tech_stack = set()
        
        # File-based detection
        for file_path in self.files.keys():
            if file_path.endswith('.py'):
                tech_stack.add('Python')
            elif file_path.endswith(('.ts', '.tsx')):
                tech_stack.add('TypeScript')
            elif file_path.endswith(('.js', '.jsx')):
                tech_stack.add('JavaScript')
            elif file_path.endswith('.java'):
                tech_stack.add('Java')
            elif file_path.endswith('.go'):
                tech_stack.add('Go')
            elif file_path.endswith('.rs'):
                tech_stack.add('Rust')
        
        # Dependency-based detection
        all_deps = []
        for deps in self.dependencies.values():
            all_deps.extend(deps)
        
        dep_map = {
            'django': 'Django', 'flask': 'Flask', 'fastapi': 'FastAPI',
            'spring': 'Spring', 'react': 'React', 'vue': 'Vue',
            'angular': 'Angular', 'nextjs': 'Next.js', 'postgresql': 'PostgreSQL',
            'mongodb': 'MongoDB', 'redis': 'Redis', 'docker': 'Docker'
        }
        
        for dep, tech in dep_map.items():
            if any(dep.lower() in d.lower() for d in all_deps):
                tech_stack.add(tech)
        
        return list(tech_stack)
    
    def _detect_project_type(self) -> str:
        """Detect project type."""
        has_django = any('django' in f.lower() for f in self.dependencies.get('python', []))
        has_flask = any('flask' in f.lower() for f in self.dependencies.get('python', []))
        has_fastapi = any('fastapi' in f.lower() for f in self.dependencies.get('python', []))
        has_react = any('react' in f.lower() for f in self.dependencies.get('npm', []))
        has_spring = any('spring' in f.lower() for f in self.dependencies.get('maven', []))
        
        if has_django or has_flask or has_fastapi or has_spring:
            return 'Backend API'
        elif has_react:
            return 'Frontend Application'
        elif any('requirements.txt' in f for f in self.files.keys()):
            return 'Python Project'
        elif any('package.json' in f for f in self.files.keys()):
            return 'Node.js Project'
        else:
            return 'Mixed Project'
    
    def get_file_content(self, file_path: str) -> str:
        """Get content of specific file."""
        return self.files.get(file_path, '')
    
    def get_files_by_extension(self, extension: str) -> List[str]:
        """Get all files of specific extension."""
        return [f for f in self.files.keys() if f.endswith(extension)]
    
    def get_summary(self) -> Dict:
        """Get codebase summary."""
        return {
            'total_files': len(self.files),
            'total_lines': sum(len(content.split('\n')) for content in self.files.values()),
            'important_files': self.important_files,
            'tech_stack': self._detect_tech_stack(),
            'project_type': self._detect_project_type(),
            'dependencies': self.dependencies,
            'file_extensions': list(set(Path(f).suffix for f in self.files.keys()))
        }
