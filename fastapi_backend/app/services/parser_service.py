import os

IGNORE_DIRS = {
    "node_modules",
    ".git",
    "venv",
    "__pycache__",
    "build",
    "dist",
    ".idea",
    "coverage",
    ".dart_tool",
    ".gradle",
    "migrations",
    "tests",
}

IGNORE_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "pubspec.lock",
    "__init__.py",
}

ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".dart",
    ".java",
    ".cpp",
    ".c",
    ".go",
    ".rs",
    ".kt",
    ".swift",
    ".yaml",
    ".yml",
    ".json",
    ".md",
}

PRIORITY_KEYWORDS = {
    "auth": 100,
    "login": 90,
    "security": 90,
    "middleware": 85,
    "api": 80,
    "route": 80,
    "controller": 75,
    "service": 70,
    "model": 70,
    "config": 65,
    "database": 65,
    "db": 65,
    "payment": 60,
}

LOW_PRIORITY = {"test": -40, "docs": -30, "assets": -50, "image": -50, "example": -20}

MAX_SIZE = 500 * 1024
MAX_FILES = 150


def score_file(path):
    score = 0
    path_lower = path.lower()

    for keyword, value in PRIORITY_KEYWORDS.items():
        if keyword in path_lower:
            score += value

    for keyword, penalty in LOW_PRIORITY.items():
        if keyword in path_lower:
            score += penalty

    return score


def get_relevant_files(repo_path):
    collected = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if file in IGNORE_FILES:
                continue

            full_path = os.path.join(root, file)

            if os.path.getsize(full_path) > MAX_SIZE:
                continue

            ext = os.path.splitext(file)[1].lower()

            if ext not in ALLOWED_EXTENSIONS:
                continue

            collected.append(full_path)

    ranked = sorted(collected, key=score_file, reverse=True)

    return ranked[:MAX_FILES]
