import json

import pytest

from app.config import ResourceConfig, load_resource_config


def test_load_resource_config_success(tmp_path) -> None:
    resource = tmp_path / "resource.json"
    resource.write_text(
        json.dumps(
            {
                "github_token": "gh",
                "cloudflare_token": "cf",
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
        cloudflare_token="cf",
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
                "cloudflare_token": "cf",
                "code": "abc",
                "email": "mail@example.com",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="github_owner"):
        load_resource_config(str(resource))
