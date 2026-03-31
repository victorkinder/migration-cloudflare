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

0. Configurar credenciais locais (nao commitar):

```bash
cp resource.example.json resource.json
```

Edite `resource.json` com seu token GitHub, e-mail, chave de migracao e URLs reais.

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
https://n8nwh.minerx.work/webhook/cloudflare-account-id {"token":""}
https://adsx66.postman.co/workspace/adsxn8n~a8478276-6c94-47e8-8ab7-bd33a86bdfd5/request/2981627-69fe700e-a848-4f5b-a2e5-b8292740af61?tab=body

api_keys.cloudflare_account_id:"" 

Frontend -> Remover e Adicionar Token da Cloudflare (para salvar a accountid da cloudflare) (ou obter do backend + postaman)
migration-cloudflare -> Preencher dados do resource
migration-cloudflare -> Executar clonagem  (python -m app.main clone)
migration-cloudflare -> Verificar clonados e apagar caso algum não faça sentido
migration-cloudflare -> Executar upload (python -m app.main migrate)

Cloudflare do cliente -> Desabilitar o deploy automático
Backend -> Adicionar a flag no backend (deploy_strategy: "cloudflare_direct")  
Frontend  -> Relogar (para que passe a enxergar o novo fluxo)
Frontend -> criar uma presell no lado do cliente para teste final.



Setar a variavel de ambiente:

- `firebase use [dev/prod]`


