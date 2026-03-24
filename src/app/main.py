from __future__ import annotations

from pathlib import Path

from app.config import ResourceConfig, load_resource_config
from app.github_client import (
    clone_repositories,
    filter_repositories,
    list_repositories,
    read_project_files,
)
from app.notifier import send_migration_data


def _sanitize_project_name(repo_name: str) -> str:
    """Converts repo name to Cloudflare project name (dots → dashes)."""
    return repo_name.replace(".", "-")


def run_migration(config: ResourceConfig) -> None:
    target_directory = Path(config.code)

    print("Listando repositórios do GitHub...")
    all_repositories = list_repositories(config.github_token, config.github_owner)

    repositories = filter_repositories(all_repositories, config.to_migrate)
    print(f"{len(repositories)} repositório(s) selecionado(s) para migração.")

    clone_repositories(repositories, target_directory, github_token=config.github_token)

    for repo in repositories:
        repo_name = repo.get("name", "")
        if not repo_name:
            continue

        repo_path = target_directory / repo_name
        if not repo_path.exists():
            print(f"[SKIP] {repo_name}: diretório não encontrado após clone.")
            continue

        files = read_project_files(repo_path)
        if not files:
            print(f"[SKIP] {repo_name}: nenhum arquivo HTML encontrado.")
            continue

        project_name = _sanitize_project_name(repo_name)
        print(f"[{repo_name}] Migrando {len(files)} arquivo(s) → projeto '{project_name}'...")

        try:
            result = send_migration_data(
                email=config.email,
                project_name=project_name,
                files=files,
                migration_url=config.migration_url,
                migration_key=config.migration_key,
            )
            print(f"[{repo_name}] ✓ {result.get('persistedFiles', '?')} arquivo(s) persistido(s).")
        except Exception as exc:
            print(f"[{repo_name}] ✗ Erro: {exc}")


def main() -> None:
    config = load_resource_config("resource.json")
    run_migration(config)


if __name__ == "__main__":
    main()
