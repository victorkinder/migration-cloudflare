import importlib
from pathlib import Path

from app.config import ResourceConfig


def make_config(**overrides) -> ResourceConfig:
    defaults = dict(
        github_token="gh",
        cloudflare_token="cf",
        github_owner="my-owner",
        code="./repos",
        email="user@example.com",
        migration_key="secret",
        migration_url="https://example.com/migrate",
        to_migrate=["repo1"],
    )
    defaults.update(overrides)
    return ResourceConfig(**defaults)


def test_run_migration_orchestrates_calls(monkeypatch, tmp_path: Path) -> None:
    main_module = importlib.import_module("app.main")
    called = {"list": False, "filter": False, "clone": False, "read": False, "notify": False}

    fake_files = {"/index.html": "<h1>ok</h1>"}

    def fake_list_repositories(token, owner):
        called["list"] = True
        return [{"name": "repo1", "clone_url": "https://x/repo1.git"}]

    def fake_filter_repositories(repositories, to_migrate):
        called["filter"] = True
        return repositories

    def fake_clone_repositories(repositories, target_root, github_token):
        called["clone"] = True
        # simulate cloned repo dir
        (Path(target_root) / "repo1").mkdir(parents=True, exist_ok=True)

    def fake_read_project_files(repo_path):
        called["read"] = True
        return fake_files

    def fake_send_migration_data(email, project_name, files, migration_url, migration_key):
        called["notify"] = True
        assert email == "user@example.com"
        assert project_name == "repo1"
        assert files == fake_files
        return {"success": True, "persistedFiles": 1}

    monkeypatch.setattr(main_module, "list_repositories", fake_list_repositories)
    monkeypatch.setattr(main_module, "filter_repositories", fake_filter_repositories)
    monkeypatch.setattr(main_module, "clone_repositories", fake_clone_repositories)
    monkeypatch.setattr(main_module, "read_project_files", fake_read_project_files)
    monkeypatch.setattr(main_module, "send_migration_data", fake_send_migration_data)

    config = make_config(code=str(tmp_path))
    main_module.run_migration(config)

    assert all(called.values()), f"Not all steps were called: {called}"


def test_run_migration_skips_repo_with_no_files(monkeypatch, tmp_path: Path) -> None:
    main_module = importlib.import_module("app.main")
    notify_called = {"value": False}

    monkeypatch.setattr(main_module, "list_repositories", lambda *a: [{"name": "repo1"}])
    monkeypatch.setattr(main_module, "filter_repositories", lambda r, _: r)
    monkeypatch.setattr(
        main_module,
        "clone_repositories",
        lambda repos, path, github_token: (Path(path) / "repo1").mkdir(parents=True, exist_ok=True),
    )
    monkeypatch.setattr(main_module, "read_project_files", lambda _: {})
    monkeypatch.setattr(
        main_module,
        "send_migration_data",
        lambda **kw: notify_called.__setitem__("value", True),
    )

    config = make_config(code=str(tmp_path))
    main_module.run_migration(config)

    assert not notify_called["value"]
