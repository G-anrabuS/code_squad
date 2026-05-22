import os
import shutil
import stat
from urllib.parse import urlparse
from git import Repo
from git.exc import GitCommandError

TEMP_REPO_DIR = "temp_repos"


def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _sanitize_repo_path(owner: str, repo_name: str) -> str:
    return f"{owner}_{repo_name}".replace('/', '_')


def clone_repo(username: str, repo_name: str, token: str, branch: str = "main"):
    os.makedirs(TEMP_REPO_DIR, exist_ok=True)

    repo_path = os.path.join(TEMP_REPO_DIR, _sanitize_repo_path(username, repo_name))

    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=remove_readonly)

    clone_url = f"https://{token}@github.com/{username}/{repo_name}.git"
    Repo.clone_from(clone_url, repo_path, branch=branch)
    return repo_path


def clone_repo_from_url(repo_url: str, token: str = None, branch: str = "main"):
    parsed = urlparse(repo_url)
    host = parsed.netloc.lower()
    path = parsed.path.strip('/')

    if host not in {"github.com", "www.github.com"}:
        raise ValueError("Only GitHub URLs are supported for public repo cloning.")

    if path.endswith('.git'):
        path = path[:-4]

    parts = path.split('/')
    if len(parts) < 2:
        raise ValueError("GitHub URL must include owner and repository name.")

    owner, repo_name = parts[0], parts[1]
    os.makedirs(TEMP_REPO_DIR, exist_ok=True)

    repo_path = os.path.join(TEMP_REPO_DIR, _sanitize_repo_path(owner, repo_name))
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=remove_readonly)

    if token:
        clone_url = f"https://{token}@github.com/{owner}/{repo_name}.git"
    else:
        clone_url = f"https://github.com/{owner}/{repo_name}.git"

    try:
        if branch:
            Repo.clone_from(clone_url, repo_path, branch=branch)
        else:
            Repo.clone_from(clone_url, repo_path)
    except GitCommandError as exc:
        if branch and 'Remote branch' in str(exc) and 'not found' in str(exc):
            try:
                Repo.clone_from(clone_url, repo_path, branch='master')
            except GitCommandError:
                Repo.clone_from(clone_url, repo_path)
        else:
            raise

    return repo_path
