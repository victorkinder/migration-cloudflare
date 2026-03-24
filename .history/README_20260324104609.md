# Projeto Python Base

Esqueleto inicial para desenvolvimento Python com estrutura `src` e testes com `pytest`.

## Objetivo
Através de 2 comandos de execução:
Comando 1 - Clonar todos os repositorios do github do token configurado em resource
Comando 2 - Enviar diretoripos/repo para backend para um endpoint temporario proprio para migração que deverá apenas armazenar os arquivos e dados no nosso lado/backend 


## Estrutura

- `src/app`: codigo da aplicacao
- `tests`: testes automatizados
- `docs/architecture`: documentacao de arquitetura

## Como executar

1. Criar ambiente virtual:

```bash
python -m venv .venv
```

2. Ativar ambiente virtual:

- Windows (PowerShell):

```bash
.venv\Scripts\Activate.ps1
```

3. Instalar dependencias de desenvolvimento:

```bash
pip install -e ".[dev]"
```

4. Rodar testes:

```bash
pytest
```
