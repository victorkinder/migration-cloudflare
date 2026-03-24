import json

import pytest

from app.config import ResourceConfig, load_resource_config


def test_load_resource_config_success(tmp_path) -> None:
    resource = tmp_path / "resource.json"
    resource.write_text(
        json.dumps(
            {
                "github_token": "gh",
                "github_owner": "owner",
                "code": "abc",
                "email": "mail@example.com",
                "migration_key": "secret",
                "migration_url": "https://example.com/migrate",
                "to_migrate": ["repo1"],
            }
        ),
        encoding="utf-8",
    )

    config = load_resource_config(str(resource))

    assert config == ResourceConfig(
        github_token="gh",
        github_owner="owner",
        code="abc",
        email="mail@example.com",
        migration_key="secret",
        migration_url="https://example.com/migrate",
        to_migrate=["repo1"],
    )


def test_load_resource_config_missing_field(tmp_path) -> None:
    resource = tmp_path / "resource.json"
    resource.write_text(
        json.dumps(
            {
                "github_token": "gh",
                "code": "abc",
                "email": "mail@example.com",
                "migration_url": "https://example.com/migrate",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="migration_key"):
        load_resource_config(str(resource))


def test_load_resource_config_ignores_extra_fields(tmp_path) -> None:
    resource = tmp_path / "resource.json"
    resource.write_text(
        json.dumps(
            {
                "github_token": "gh",
                "github_owner": "owner",
                "code": "abc",
                "email": "mail@example.com",
                "migration_key": "secret",
                "migration_url": "https://example.com/migrate",
                "cloudflare_token": "cf-token",
            }
        ),
        encoding="utf-8",
    )

    config = load_resource_config(str(resource))
    assert config.github_token == "gh"
