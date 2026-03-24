from pathlib import Path
from unittest.mock import Mock

from app.github_client import (
    clone_repositories,
    filter_repositories,
    list_repositories,
    read_project_files,
)


def test_list_repositories_paginates(monkeypatch) -> None:
    responses = [
        [{"name": "repo1", "clone_url": "https://x/repo1.git"}],
        [],
    ]
    call_index = {"value": 0}

    def fake_get(url, headers, params, timeout):
        response = Mock()
        response.raise_for_status = Mock()
        response.json = Mock(return_value=responses[call_index["value"]])
        call_index["value"] += 1
        return response

    monkeypatch.setattr("app.github_client.requests.get", fake_get)

    repos = list_repositories("token", "owner")
    assert repos == [{"name": "repo1", "clone_url": "https://x/repo1.git"}]


def test_filter_repositories_by_to_migrate() -> None:
    repos = [
        {"name": "a", "clone_url": "https://x/a.git"},
        {"name": "b", "clone_url": "https://x/b.git"},
        {"name": "c", "clone_url": "https://x/c.git"},
    ]
    result = filter_repositories(repos, ["a", "c"])
    assert [r["name"] for r in result] == ["a", "c"]


def test_filter_repositories_returns_all_when_empty() -> None:
    repos = [{"name": "a"}, {"name": "b"}]
    assert filter_repositories(repos, []) == repos


def test_clone_repositories_uses_authenticated_url(monkeypatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd, check, capture_output, text):
        calls.append(cmd)
        return Mock()

    monkeypatch.setattr("app.github_client.subprocess.run", fake_run)
    repos = [{"name": "repo1", "clone_url": "https://github.com/owner/repo1.git"}]

    clone_repositories(repos, tmp_path / "code", github_token="mytoken")

    assert calls
    assert "https://mytoken@github.com/owner/repo1.git" in calls[0]


def test_clone_repositories_skips_existing(monkeypatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    monkeypatch.setattr(
        "app.github_client.subprocess.run",
        lambda cmd, **kw: calls.append(cmd) or Mock(),
    )

    existing = tmp_path / "repo1"
    existing.mkdir()
    repos = [{"name": "repo1", "clone_url": "https://x/repo1.git"}]

    clone_repositories(repos, tmp_path, github_token="token")

    assert calls == []


def test_read_project_files_returns_html_files(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text("<h1>root</h1>", encoding="utf-8")
    (tmp_path / "slug").mkdir()
    (tmp_path / "slug" / "index.html").write_text("<h1>slug</h1>", encoding="utf-8")
    (tmp_path / "robots.txt").write_text("User-agent: *", encoding="utf-8")

    files = read_project_files(tmp_path)

    assert files["/index.html"] == "<h1>root</h1>"
    assert files["/slug/index.html"] == "<h1>slug</h1>"
    assert files["/robots.txt"] == "User-agent: *"


def test_read_project_files_skips_git_and_non_html(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("gitconfig", encoding="utf-8")
    (tmp_path / "README.md").write_text("# readme", encoding="utf-8")
    (tmp_path / "index.html").write_text("<h1>ok</h1>", encoding="utf-8")

    files = read_project_files(tmp_path)

    assert "/index.html" in files
    assert "/.git/config" not in files
    assert "/README.md" not in files
