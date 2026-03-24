from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ResourceConfig:
    github_token: str
    cloudflare_token: str
    github_owner: str
    code: str
    email: str
    migration_key: str
    migration_url: str
    to_migrate: list[str] = field(default_factory=list)


REQUIRED_FIELDS = (
    "github_token",
    "cloudflare_token",
    "github_owner",
    "code",
    "email",
    "migration_key",
    "migration_url",
)


def load_resource_config(resource_path: str = "resource.json") -> ResourceConfig:
    file_path = Path(resource_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Resource file not found: {resource_path}")

    data = json.loads(file_path.read_text(encoding="utf-8"))
    missing = [field for field in REQUIRED_FIELDS if not str(data.get(field, "")).strip()]
    if missing:
        raise ValueError(f"Missing required resource field(s): {', '.join(missing)}")

    return ResourceConfig(
        github_token=data["github_token"].strip(),
        cloudflare_token=data["cloudflare_token"].strip(),
        github_owner=data["github_owner"].strip(),
        code=data["code"].strip(),
        email=data["email"].strip(),
        migration_key=data["migration_key"].strip(),
        migration_url=data["migration_url"].strip(),
        to_migrate=list(data.get("to_migrate", [])),
    )
