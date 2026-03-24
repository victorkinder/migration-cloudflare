from __future__ import annotations

import subprocess
from pathlib import Path

import requests

ALLOWED_EXTENSIONS = {".html", ".txt"}
ALLOWED_FILENAMES = {"robots.txt"}


def get_authenticated_owner(github_token: str) -> str:
    """Returns the login (username) of the authenticated GitHub token owner."""
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.get("https://api.github.com/user", headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()["login"]


def list_repositories(github_token: str, owner: str) -> list[dict]:
    repos: list[dict] = []
    page = 1
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    while True:
        response = requests.get(
            f"https://api.github.com/users/{owner}/repos",
            headers=headers,
            params={"per_page": 100, "page": page},
            timeout=30,
        )
        response.raise_for_status()
        page_items = response.json()
        if not page_items:
            break
        repos.extend(page_items)
        if len(page_items) < 100:
            break
        page += 1

    return repos


def filter_repositories(repositories: list[dict], to_migrate: list[str]) -> list[dict]:
    """Returns only repos whose name is in to_migrate. Returns all if to_migrate is empty."""
    if not to_migrate:
        return repositories
    allowed = set(to_migrate)
    return [r for r in repositories if r.get("name") in allowed]


def _authenticated_clone_url(clone_url: str, github_token: str) -> str:
    """Injects the GitHub token into the HTTPS clone URL for private repo access."""
    if clone_url.startswith("https://"):
        return clone_url.replace("https://", f"https://{github_token}@", 1)
    return clone_url


def clone_repositories(
    repositories: list[dict],
    target_root: Path,
    github_token: str = "",
) -> None:
    target_root.mkdir(parents=True, exist_ok=True)
    for repo in repositories:
        clone_url = repo.get("clone_url")
        repo_name = repo.get("name")
        if not clone_url or not repo_name:
            continue

        destination = target_root / repo_name
        if destination.exists():
            continue

        auth_url = _authenticated_clone_url(clone_url, github_token) if github_token else clone_url

        subprocess.run(
            ["git", "clone", auth_url, str(destination)],
            check=True,
            capture_output=True,
            text=True,
        )


def read_project_files(repo_path: Path) -> dict[str, str]:
    """
    Reads all deployable files from a cloned repo directory.
    Returns a dict mapping "/relative/path" -> file content (str).
    Skips .git and non-HTML/txt files.
    """
    files: dict[str, str] = {}

    for file_path in sorted(repo_path.rglob("*")):
        if not file_path.is_file():
            continue

        relative = file_path.relative_to(repo_path)

        # Skip hidden dirs and .git
        if any(part.startswith(".") for part in relative.parts):
            continue

        suffix = file_path.suffix.lower()
        name = file_path.name.lower()

        if suffix not in ALLOWED_EXTENSIONS and name not in ALLOWED_FILENAMES:
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        manifest_path = "/" + relative.as_posix()
        files[manifest_path] = content

    return files
