# Microserviço de Chamados

O serviço executa sua própria API FastAPI e persiste chamados e comentários em
um PostgreSQL exclusivo. IDs de usuários e ativos são referências lógicas:
Chamados não acessa os bancos dos outros serviços nem cria chaves estrangeiras
para tabelas externas.

## Configuração e execução

Use Docker e Docker Compose v2. Configure `microservices/chamados/.env` com o
mesmo `JWT_SEGREDO` configurado em Usuários e Inventário e credenciais próprias
para o banco deste serviço. O exemplo pode ser copiado com:

```bash
cp -n microservices/chamados/.env.example microservices/chamados/.env
```

Crie uma única vez a rede compartilhada para as APIs:

```bash
docker network create helpdesk-rede
```

Inicie API e banco a partir da raiz do repositório:

```bash
docker compose --env-file microservices/chamados/.env \
  -f microservices/chamados/docker-compose.yml up --build
```

A API e o banco não publicam portas para o host; a API expõe a porta `8000`
somente para comunicação interna na rede Docker. Acesse-a pelo gateway. As
rotas `GET /health` e `GET /saude` verificam a saúde da API.

Os Compose de Chamados, Usuários e Inventário conectam suas APIs à rede externa
`helpdesk-rede`; os bancos continuam em redes separadas. Suba os três serviços
para que Chamados possa validar técnicos e ativos. As URLs padrão são
`http://usuarios:8000` e `http://inventario:8000`. As chamadas têm timeout
configurável por `TIMEOUT_SERVICOS_SEGUNDOS` (padrão: 2 segundos) e repassam o
token Bearer do usuário. Falhas de conexão ou timeout retornam HTTP 503; uma
resposta inválida do serviço dependente retorna HTTP 502.

## API

Todas as rotas de chamados exigem um JWT Bearer válido, verificado por este
serviço com o segredo compartilhado. O serviço mantém as regras de perfil e
visibilidade do sistema:

- `POST /chamados`: abre chamado; valida o ativo no Inventário quando informado.
- `GET /chamados` e `GET /chamados/{id}`: solicitantes veem apenas os próprios
  chamados; técnicos e administradores podem ver todos.
- `GET /chamados/painel`: retorna totais e chamados atrasados conforme o perfil.
- `PATCH /chamados/{id}/atribuir`: valida o técnico no serviço de Usuários.
- `PATCH /chamados/{id}/status`: aplica as transições permitidas.
- `POST /chamados/{id}/comentarios`: adiciona comentário, exceto em chamado
  fechado.

O SLA continua sendo de 4h (crítica), 8h (alta), 24h (média) e 72h (baixa).
Para iniciar o atendimento, é necessário atribuir um técnico. Chamados
resolvidos podem ser fechados ou reabertos; chamados fechados não aceitam novos
comentários.
