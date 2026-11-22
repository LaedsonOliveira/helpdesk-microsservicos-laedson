# Microserviço de Usuários

Este serviço pode ser executado isoladamente do monólito. A API e o PostgreSQL
rodam em contêineres próprios; o banco não publica uma porta no computador.

## Pré-requisitos

- Docker instalado e em execução.
- Docker Compose v2 (`docker compose`).

## Configuração

Na raiz do repositório, copie o exemplo para criar a configuração local:

```bash
cp -n microservices/usuarios/.env.example microservices/usuarios/.env
```

Gere um segredo para os tokens:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Edite `microservices/usuarios/.env` e cole o valor gerado em `JWT_SEGREDO`.
Configure também `ADMIN_EMAIL`, `ADMIN_PASSWORD` e as credenciais do PostgreSQL.
O segredo JWT deve ter pelo menos 32 caracteres. Não compartilhe nem envie o
arquivo `.env` ao Git.

## Subir API e banco

Execute da raiz do repositório:

```bash
docker compose --env-file microservices/usuarios/.env \
  -f microservices/usuarios/docker-compose.yml up --build
```

Para verificar o estado dos contêineres, em outro terminal:

```bash
docker compose --env-file microservices/usuarios/.env \
  -f microservices/usuarios/docker-compose.yml ps
```

A API fica acessível em `http://localhost:8001`; o PostgreSQL só é acessível
pela rede interna do Docker. A tabela é criada ao iniciar a aplicação. O
administrador inicial usa `ADMIN_EMAIL` e `ADMIN_PASSWORD` e só é criado se o
banco ainda não tiver usuários.

## Testar a API

Verifique se a aplicação está saudável:

```bash
curl -i http://localhost:8001/health
```

Faça login usando os valores definidos para `ADMIN_EMAIL` e `ADMIN_PASSWORD`:

```bash
curl -i -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@empresa.com","senha":"Helpdesk2026"}'
```

Copie o `access_token` da resposta e use-o nas rotas protegidas:

```bash
curl -i http://localhost:8001/usuarios \
  -H "Authorization: Bearer <TOKEN>"
```

Crie um usuário com token de administrador:

```bash
curl -i -X POST http://localhost:8001/usuarios \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"nome":"Carla Dias","email":"carla@empresa.com","perfil":"tecnico","senha":"Helpdesk2026"}'
```

Substitua as credenciais de exemplo dos comandos pelos valores do seu `.env` se
você os alterou. A documentação interativa também está em
`http://localhost:8001/docs`.

Rotas disponíveis:

- `GET /health`: saúde da API.
- `POST /auth/login`: login e emissão de JWT.
- `GET /auth/eu`: dados do usuário autenticado.
- `GET /usuarios` e `GET /usuarios/{id}`: exigem token Bearer.
- `POST /usuarios`: exige token Bearer de administrador.

## Parar o serviço

```bash
docker compose --env-file microservices/usuarios/.env \
  -f microservices/usuarios/docker-compose.yml down
```

Os dados ficam no volume `usuarios_dados` e são mantidos ao parar os
contêineres. Para apagar o banco local e recriá-lo do zero, use
`docker compose ... down --volumes`; isso remove permanentemente os dados desse
volume.

## Testes automatizados

Os testes da API usam SQLite em memória e não precisam do Docker:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r microservices/usuarios/requirements.txt -r requirements-dev.txt
python -m pytest -q microservices/usuarios/tests
```

A inicialização atual cria tabelas para facilitar a extração inicial. Antes de
evoluir o serviço ou manter dados importantes, substitua `create_all` por
migrações versionadas.
