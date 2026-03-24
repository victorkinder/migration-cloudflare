from __future__ import annotations

import requests


def send_migration_data(
    email: str,
    project_name: str,
    files: dict[str, str],
    migration_url: str,
    migration_key: str,
) -> dict:
    """
    Sends project files to the backend migration endpoint.
    Returns the parsed JSON response.
    """
    response = requests.post(
        migration_url,
        json={
            "migration_key": migration_key,
            "email": email,
            "projectName": project_name,
            "files": files,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()
