# Microserviço de Usuários

Este serviço é uma primeira extração independente do monólito. Ele mantém seu
próprio banco PostgreSQL, autenticação JWT e rotas de usuários.

## Executar com Docker Compose

Na raiz do repositório, copie `.env.example` para `.env` neste diretório e
substitua `JWT_SEGREDO` e as credenciais do banco por valores locais:

```bash
cp microservices/usuarios/.env.example microservices/usuarios/.env
docker compose --env-file microservices/usuarios/.env \
  -f microservices/usuarios/docker-compose.yml up --build
```

O serviço fica disponível em `http://localhost:8001`; o PostgreSQL não publica
porta no host. O administrador inicial é criado somente se o banco estiver
vazio e `ADMIN_EMAIL`/`ADMIN_PASSWORD` estiverem definidos. Altere as credenciais
de exemplo antes de usar fora de um ambiente local de aula.

## Rotas para o primeiro teste

- `GET /health`: verifica se a aplicação está respondendo.
- `POST /auth/login`: recebe `{"email":"admin@empresa.com","senha":"Helpdesk2026"}` e devolve um JWT.
- `GET /auth/eu`: retorna o usuário autenticado.
- `GET /usuarios` e `GET /usuarios/{id}`: exigem token Bearer.
- `POST /usuarios`: exige token Bearer de administrador.

Exemplo de criação de usuário:

```bash
curl -X POST http://localhost:8001/usuarios \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"nome":"Carla Dias","email":"carla@empresa.com","perfil":"tecnico","senha":"Helpdesk2026"}'
```

As tabelas são criadas ao iniciar a aplicação para facilitar o primeiro teste.
Antes de evoluir o serviço ou manter dados em produção, deve-se substituir essa
inicialização simples por migrações versionadas.
