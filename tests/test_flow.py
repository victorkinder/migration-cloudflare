import importlib
from pathlib import Path

from app.config import ResourceConfig


def make_config(**overrides) -> ResourceConfig:
    defaults = dict(
        github_token="gh",
        github_owner="my-owner",
        code="./repos",
        email="user@example.com",
        migration_key="secret",
        migration_url="https://example.com/migrate",
        to_migrate=[],
    )
    defaults.update(overrides)
    return ResourceConfig(**defaults)


def test_clone_filters_by_to_migrate_when_set(monkeypatch, tmp_path: Path) -> None:
    main_module = importlib.import_module("app.main")
    cloned_repos = {}

    monkeypatch.setattr(
        main_module,
        "list_repositories",
        lambda *a: [{"name": "repo1"}, {"name": "repo2"}, {"name": "repo3"}],
    )

    def fake_clone(repositories, target_root, github_token):
        cloned_repos["names"] = [r["name"] for r in repositories]

    monkeypatch.setattr(main_module, "clone_repositories", fake_clone)

    config = make_config(code=str(tmp_path), to_migrate=["repo1", "repo3"])
    main_module.clone(config)

    assert cloned_repos["names"] == ["repo1", "repo3"]


def test_clone_clones_all_when_to_migrate_empty(monkeypatch, tmp_path: Path) -> None:
    main_module = importlib.import_module("app.main")
    cloned_repos = {}

    monkeypatch.setattr(
        main_module,
        "list_repositories",
        lambda *a: [{"name": "repo1"}, {"name": "repo2"}],
    )

    def fake_clone(repositories, target_root, github_token):
        cloned_repos["names"] = [r["name"] for r in repositories]

    monkeypatch.setattr(main_module, "clone_repositories", fake_clone)

    config = make_config(code=str(tmp_path), to_migrate=[])
    main_module.clone(config)

    assert cloned_repos["names"] == ["repo1", "repo2"]


def test_migrate_processes_all_cloned_dirs(monkeypatch, tmp_path: Path) -> None:
    main_module = importlib.import_module("app.main")
    migrated = []

    (tmp_path / "repo1").mkdir()
    (tmp_path / "repo2").mkdir()

    monkeypatch.setattr(main_module, "read_project_files", lambda _: {"/index.html": "<h1>ok</h1>"})

    def fake_send(email, project_name, files, migration_url, migration_key):
        migrated.append(project_name)
        return {"success": True, "persistedFiles": 1}

    monkeypatch.setattr(main_module, "send_migration_data", fake_send)

    config = make_config(code=str(tmp_path))
    main_module.migrate(config)

    assert set(migrated) == {"repo1", "repo2"}


def test_migrate_skips_repo_with_no_files(monkeypatch, tmp_path: Path) -> None:
    main_module = importlib.import_module("app.main")
    notify_called = {"value": False}

    (tmp_path / "repo1").mkdir()

    monkeypatch.setattr(main_module, "read_project_files", lambda _: {})
    monkeypatch.setattr(
        main_module,
        "send_migration_data",
        lambda **kw: notify_called.__setitem__("value", True),
    )

    config = make_config(code=str(tmp_path))
    main_module.migrate(config)

    assert not notify_called["value"]


def test_migrate_aborts_when_no_clone_dir(monkeypatch, tmp_path: Path) -> None:
    main_module = importlib.import_module("app.main")
    notify_called = {"value": False}

    monkeypatch.setattr(
        main_module,
        "send_migration_data",
        lambda **kw: notify_called.__setitem__("value", True),
    )

    config = make_config(code=str(tmp_path / "does_not_exist"))
    main_module.migrate(config)

    assert not notify_called["value"]
