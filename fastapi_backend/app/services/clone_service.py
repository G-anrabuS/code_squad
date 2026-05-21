import os
import shutil
from git import Repo

TEMP_REPO_DIR = "temp_repos"


def clone_repo(username: str, repo_name: str, token: str, branch: str):
    os.makedirs(TEMP_REPO_DIR, exist_ok=True)

    repo_path = os.path.join(TEMP_REPO_DIR, repo_name)

    # clean old clone
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    clone_url = f"https://{token}@github.com/{username}/{repo_name}.git"

    Repo.clone_from(clone_url, repo_path, branch=branch)

    return repo_path
