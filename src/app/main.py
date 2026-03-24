from __future__ import annotations

import sys
import time
from pathlib import Path

from app.config import ResourceConfig, load_resource_config
from app.github_client import (
    clone_repositories,
    filter_repositories,
    get_authenticated_owner,
    list_repositories,
    read_project_files,
)
from app.notifier import send_migration_data


def _sanitize_project_name(repo_name: str) -> str:
    """Converts repo name to Cloudflare project name (dots → dashes)."""
    return repo_name.replace(".", "-")


def _resolve_owner(config: ResourceConfig) -> str:
    if config.github_owner:
        return config.github_owner
    print("github_owner não configurado. Buscando via token...")
    owner = get_authenticated_owner(config.github_token)
    print(f"Owner identificado: {owner}")
    return owner


def clone(config: ResourceConfig) -> None:
    """Comando 1: clona repositórios do GitHub.
    Se 'to_migrate' estiver preenchido, clona apenas os listados. Caso contrário, clona todos.
    """
    target_directory = Path(config.code)
    owner = _resolve_owner(config)
    print("Listando repositórios do GitHub...")
    all_repositories = list_repositories(config.github_token, owner)
    repositories = filter_repositories(all_repositories, config.to_migrate)

    label = f"{len(repositories)} repositório(s)" + (
        f" (filtrado de {len(all_repositories)})" if config.to_migrate else ""
    )
    print(f"{label} encontrado(s). Clonando...")
    clone_repositories(repositories, target_directory, github_token=config.github_token)
    print(f"Concluído. Repositórios em: {target_directory.resolve()}")
    print("Execute: python -m app.main migrate")


def migrate(config: ResourceConfig) -> None:
    """Comando 2: envia TODOS os repositórios clonados para o backend."""
    target_directory = Path(config.code)

    if not target_directory.exists():
        print(f"Diretório '{target_directory}' não encontrado. Execute 'clone' primeiro.")
        return

    cloned = [p for p in sorted(target_directory.iterdir()) if p.is_dir()]
    if not cloned:
        print("Nenhum repositório clonado encontrado. Execute 'clone' primeiro.")
        return

    print(f"{len(cloned)} repositório(s) clonado(s) encontrado(s).")

    for repo_path in cloned:
        repo_name = repo_path.name

        files = read_project_files(repo_path)
        if not files:
            print(f"[SKIP] {repo_name}: nenhum arquivo HTML encontrado.")
            continue

        project_name = _sanitize_project_name(repo_name)
        print(f"[{repo_name}] {len(files)} arquivo(s) encontrado(s) → projeto '{project_name}'.")

        # Split: root files (depth 1) vs subdirectory groups
        root_files = {p: c for p, c in files.items() if p.count("/") == 1}
        subdirs: dict[str, dict[str, str]] = {}
        for path, content in files.items():
            if path.count("/") > 1:
                subdir = path.split("/")[1]
                subdirs.setdefault(subdir, {})[path] = content

        batches: list[tuple[str, dict[str, str]]] = []
        if root_files:
            batches.append(("raiz", root_files))
        for subdir, subdir_files in sorted(subdirs.items()):
            batches.append((subdir, subdir_files))

        total_persisted = 0
        for i, (label, batch_files) in enumerate(batches):
            if i > 0:
                time.sleep(2)
            try:
                result = send_migration_data(
                    email=config.email,
                    project_name=project_name,
                    files=batch_files,
                    migration_url=config.migration_url,
                    migration_key=config.migration_key,
                )
                persisted = result.get("persistedFiles", 0)
                total_persisted += persisted
                print(f"  [{label}] ✓ {persisted} arquivo(s).")
            except Exception as exc:
                print(f"  [{label}] ✗ Erro: {exc}")

        print(f"[{repo_name}] Concluído: {total_persisted}/{len(files)} arquivo(s) persistido(s).")


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command not in ("clone", "migrate"):
        print("Uso: python -m app.main <clone|migrate>")
        print("  clone   — clona todos os repositórios do GitHub")
        print("  migrate — envia os repositórios de 'to_migrate' para o backend")
        sys.exit(1)

    config = load_resource_config("resource.json")
    if command == "clone":
        clone(config)
    else:
        migrate(config)


if __name__ == "__main__":
    main()
