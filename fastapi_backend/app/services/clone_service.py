import os
import shutil
import stat
import tempfile
from urllib.parse import urlparse

from git import Repo
from git.exc import GitCommandError


def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def cleanup_repo(repo_path: str):
    """
    Safely delete a cloned temporary repository.
    """
    if repo_path and os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=remove_readonly)


def _create_temp_repo_path(owner: str, repo_name: str) -> str:
    """
    Create a unique temporary directory for repo cloning.
    Example:
        /tmp/google_gemini_x82kd9
    """
    safe_name = f"{owner}_{repo_name}".replace("/", "_")
    return tempfile.mkdtemp(prefix=f"{safe_name}_")


def clone_repo(
    username: str,
    repo_name: str,
    token: str,
    branch: str = "main",
) -> str:
    """
    Clone a private GitHub repository using username/repo_name.
    """
    repo_path = _create_temp_repo_path(username, repo_name)
    clone_url = f"https://{token}@github.com/{username}/{repo_name}.git"

    try:
        Repo.clone_from(clone_url, repo_path, branch=branch)
        return repo_path

    except GitCommandError as exc:
        if branch and "Remote branch" in str(exc) and "not found" in str(exc):
            try:
                Repo.clone_from(clone_url, repo_path, branch="master")
                return repo_path
            except Exception:
                cleanup_repo(repo_path)
                raise

        cleanup_repo(repo_path)
        raise

    except Exception:
        cleanup_repo(repo_path)
        raise


def clone_repo_from_url(
    repo_url: str,
    token: str | None = None,
    branch: str = "main",
) -> str:
    """
    Clone a GitHub repository from URL.

    Supports:
    - public repos
    - private repos (with token)
    """
    parsed = urlparse(repo_url)
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")

    if host not in {"github.com", "www.github.com"}:
        raise ValueError("Only GitHub URLs are supported.")

    if path.endswith(".git"):
        path = path[:-4]

    parts = path.split("/")
    if len(parts) < 2:
        raise ValueError("GitHub URL must include owner and repository name.")

    owner, repo_name = parts[0], parts[1]
    repo_path = _create_temp_repo_path(owner, repo_name)

    if token:
        clone_url = f"https://{token}@github.com/{owner}/{repo_name}.git"
    else:
        clone_url = f"https://github.com/{owner}/{repo_name}.git"

    try:
        if branch:
            Repo.clone_from(clone_url, repo_path, branch=branch)
        else:
            Repo.clone_from(clone_url, repo_path)

        return repo_path

    except GitCommandError as exc:
        if branch and "Remote branch" in str(exc) and "not found" in str(exc):
            try:
                Repo.clone_from(clone_url, repo_path, branch="master")
                return repo_path
            except Exception:
                cleanup_repo(repo_path)
                raise

        cleanup_repo(repo_path)
        raise

    except Exception:
        cleanup_repo(repo_path)
        raise
