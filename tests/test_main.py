from unittest.mock import patch

from fastapi.testclient import TestClient

from main import APP, LISTA_TAREFAS, METRICAS

CLIENT = TestClient(APP)


def setup_function():
    LISTA_TAREFAS.clear()

    METRICAS["quantidade_total_tarefas"] = 0
    METRICAS["quantidade_tarefas_pendentes"] = 0
    METRICAS["quantidade_tarefas_concluidas"] = 0
    METRICAS["quantidade_tarefas_atualizadas"] = 0
    METRICAS["quantidade_tarefas_removidas"] = 0
    METRICAS["tempo_medio_conclusao_segundos"] = 0


def test_index():
    resposta = CLIENT.get("/")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "message": "Bem-vindo à API de Tarefas!"
    }


def test_criar_tarefa():
    resposta = CLIENT.post(
        "/tarefas",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste",
        },
    )

    assert resposta.status_code == 201
    assert resposta.json() == {
        "message": "Tarefa criada com sucesso.",
        "id": 1,
    }


def test_nao_permitir_tarefa_duplicada():
    CLIENT.post(
        "/tarefas",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste",
        },
    )

    resposta = CLIENT.post(
        "/tarefas",
        params={
            "titulo": "TAREFA TESTE",
            "descricao": "outra descricao",
        },
    )

    assert resposta.status_code == 409
    assert resposta.json() == {
        "detail": {
            "message": "Já existe uma tarefa com esse título."
        }
    }


def test_listar_tarefa():
    CLIENT.post(
        "/tarefas",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste",
        },
    )

    resposta = CLIENT.get("/tarefas/1")

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["id"] == 1
    assert dados["titulo"] == "tarefa teste"
    assert dados["descricao"] == "descricao teste"
    assert dados["concluido"] is False
    assert dados["data_conclusao"] is None


def test_listar_tarefa_inexistente():
    resposta = CLIENT.get("/tarefas/999")

    assert resposta.status_code == 404
    assert resposta.json() == {
        "detail": {
            "message": "Tarefa não encontrada."
        }
    }


@patch("main.requests.post")
def test_atualizar_tarefa(mock_post):
    mock_post.return_value.status_code = 200

    CLIENT.post(
        "/tarefas",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste",
        },
    )

    resposta = CLIENT.put(
        "/tarefas/1",
        params={
            "titulo": "nova tarefa",
            "descricao": "nova descricao",
            "concluido": True,
        },
    )

    assert resposta.status_code == 200
    assert resposta.json() == {
        "message": "Tarefa atualizada com sucesso."
    }

    tarefa = CLIENT.get("/tarefas/1")

    assert tarefa.json()["titulo"] == "nova tarefa"
    assert tarefa.json()["descricao"] == "nova descricao"
    assert tarefa.json()["concluido"] is True
    assert tarefa.json()["data_conclusao"] is not None

    mock_post.assert_called_once()


def test_atualizar_tarefa_inexistente():
    resposta = CLIENT.put(
        "/tarefas/999",
        params={
            "titulo": "nova tarefa",
            "descricao": "nova descricao",
            "concluido": False,
        },
    )

    assert resposta.status_code == 404
    assert resposta.json() == {
        "detail": {
            "message": "Tarefa não encontrada."
        }
    }


def test_deletar_tarefa():
    CLIENT.post(
        "/tarefas",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste",
        },
    )

    resposta = CLIENT.delete("/tarefas/1")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "message": "Tarefa deletada com sucesso."
    }


def test_deletar_tarefa_inexistente():
    resposta = CLIENT.delete("/tarefas/999")

    assert resposta.status_code == 404
    assert resposta.json() == {
        "detail": {
            "message": "Tarefa não encontrada."
        }
    }


def test_health():
    resposta = CLIENT.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "message": "healthy"
    }