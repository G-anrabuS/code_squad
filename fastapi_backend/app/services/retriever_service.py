from typing import Any, Dict, List, Optional

from app.services.embedding_service import semantic_search

AGENT_FOCUS = {
    'summary': [
        'README', 'entry points', 'configuration', 'routes', 'controllers', 'main modules',
        'dependency files', 'folder structure', 'project overview',
    ],
    'judge': [
        'important files', 'large files', 'duplicated logic', 'core services',
        'data models', 'business logic',
    ],
    'architect': [
        'folder structure', 'imports', 'routes', 'services', 'models', 'configs',
        'module boundaries', 'data flow',
    ],
    'performance': [
        'loops', 'database queries', 'api calls', 'async code', 'heavy processing',
        'caching', 'memory use',
    ],
    'security': [
        '.env usage', 'authentication', 'authorization', 'middleware', 'routes',
        'configuration files', 'file upload logic', 'input validation',
    ],
}

AGENT_QUERY_TEMPLATES = {
    'summary': (
        'Retrieve a compact repository summary using README, entry points, config files, routes, '
        'controllers and main modules. Use folder structure and dependency files to explain the project.'
    ),
    'judge': (
        'Retrieve the most relevant code chunks for code quality, duplication, large services, '
        'and core business logic. Focus on important files and architecture risk areas.'
    ),
    'architect': (
        'Retrieve code chunks that show folder structure, imports, routes, services, models, '
        'and configuration patterns for architecture analysis.'
    ),
    'performance': (
        'Retrieve relevant chunks for performance analysis, including loops, database queries, '
        'API calls, async code, and heavy processing paths.'
    ),
    'security': (
        'Retrieve security-related code chunks including .env usage, auth files, middleware, '
        'routes, config, and file upload or input handling logic.'
    ),
}


def _build_agent_query(agent_name: str, repo_context: Dict[str, Any]) -> str:
    focus = AGENT_FOCUS.get(agent_name, [])
    base = AGENT_QUERY_TEMPLATES.get(agent_name, '')
    parts = [base]

    if repo_context.get('project_summary'):
        parts.append(f"Project summary: {repo_context['project_summary']}")

    if repo_context.get('entry_points'):
        parts.append(f"Entry points: {', '.join(repo_context['entry_points'][:6])}")

    if repo_context.get('important_files'):
        parts.append(f"Important files: {', '.join(repo_context['important_files'][:8])}")

    if repo_context.get('dependency_files'):
        parts.append(f"Dependency files: {', '.join(repo_context['dependency_files'])}")

    if repo_context.get('folder_tree'):
        parts.append(f"Folder tree summary: {repo_context['folder_tree']}")

    if focus:
        parts.append(f"Focus on: {', '.join(focus[:6])}")

    return '\n'.join(parts)


def retrieve_agent_chunks(
    agent_name: str,
    repo_context: Dict[str, Any],
    top_k: int = 6,
    collection_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    query = _build_agent_query(agent_name, repo_context)
    return semantic_search(
        query,
        top_k=top_k,
        collection_name=collection_name,
        repo_id=repo_context.get('repo_id'),
    )
