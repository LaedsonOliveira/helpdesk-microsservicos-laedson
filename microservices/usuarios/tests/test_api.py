import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def obter_token(client: TestClient) -> str:
    resposta = client.post(
        "/auth/login",
        json={"email": "admin@empresa.com", "senha": "Helpdesk2026"},
    )
    assert resposta.status_code == 200
    return resposta.json()["access_token"]


def test_health_e_login_inicial(client: TestClient):
    assert client.get("/health").json() == {"status": "ok"}

    resposta = client.post(
        "/auth/login",
        json={"email": "admin@empresa.com", "senha": "Helpdesk2026"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["usuario"]["perfil"] == "admin"
    assert "senha_hash" not in resposta.json()["usuario"]


def test_rotas_protegidas_e_criacao_de_usuario(client: TestClient):
    assert client.get("/usuarios").status_code == 401
    token = obter_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resposta = client.post(
        "/usuarios",
        headers=headers,
        json={
            "nome": "Carla Dias",
            "email": "CARLA@empresa.com",
            "perfil": "tecnico",
            "senha": "Helpdesk2026",
        },
    )

    assert resposta.status_code == 201
    assert resposta.json()["email"] == "carla@empresa.com"
    assert "senha_hash" not in resposta.json()
    usuario_id = resposta.json()["id"]

    assert client.get("/usuarios", headers=headers).status_code == 200
    assert client.get(f"/usuarios/{usuario_id}", headers=headers).json()["nome"] == "Carla Dias"
    assert client.get("/auth/eu", headers=headers).json()["email"] == "admin@empresa.com"

    duplicado = client.post(
        "/usuarios",
        headers=headers,
        json={
            "nome": "Carla Dias",
            "email": "carla@empresa.com",
            "perfil": "tecnico",
            "senha": "Helpdesk2026",
        },
    )
    assert duplicado.status_code == 409

    login_tecnico = client.post(
        "/auth/login",
        json={"email": "carla@empresa.com", "senha": "Helpdesk2026"},
    )
    token_tecnico = login_tecnico.json()["access_token"]
    proibido = client.post(
        "/usuarios",
        headers={"Authorization": f"Bearer {token_tecnico}"},
        json={
            "nome": "Outro usuário",
            "email": "outro@empresa.com",
            "perfil": "solicitante",
            "senha": "Helpdesk2026",
        },
    )
    assert proibido.status_code == 403


def test_login_invalido_e_usuario_inexistente(client: TestClient):
    token = obter_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resposta_login = client.post(
        "/auth/login",
        json={"email": "admin@empresa.com", "senha": "senha-incorreta"},
    )
    resposta_usuario = client.get("/usuarios/9999", headers=headers)

    assert resposta_login.status_code == 401
    assert resposta_usuario.status_code == 404
