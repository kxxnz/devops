from datetime import datetime, timedelta
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


def criar_tarefa():
    return CLIENT.post(
        "/tarefas",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste",
        },
    )


def test_metricas_iniciais():
    resposta = CLIENT.get("/metricas")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "quantidade_total_tarefas": 0,
        "quantidade_tarefas_pendentes": 0,
        "quantidade_tarefas_concluidas": 0,
        "quantidade_tarefas_atualizadas": 0,
        "quantidade_tarefas_removidas": 0,
        "tempo_medio_conclusao_segundos": 0,
    }


def test_metricas_ao_criar_tarefa():
    criar_tarefa()

    metricas = CLIENT.get("/metricas").json()

    assert metricas["quantidade_total_tarefas"] == 1
    assert metricas["quantidade_tarefas_pendentes"] == 1
    assert metricas["quantidade_tarefas_concluidas"] == 0


@patch("main.requests.post")
def test_metricas_ao_concluir_tarefa(mock_post):
    criar_tarefa()

    CLIENT.put(
        "/tarefas/1",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste",
            "concluido": True,
        },
    )

    metricas = CLIENT.get("/metricas").json()

    assert metricas["quantidade_total_tarefas"] == 1
    assert metricas["quantidade_tarefas_pendentes"] == 0
    assert metricas["quantidade_tarefas_concluidas"] == 1
    assert metricas["quantidade_tarefas_atualizadas"] == 1

    mock_post.assert_called_once()


@patch("main.requests.post")
def test_metricas_ao_reabrir_tarefa(mock_post):
    criar_tarefa()

    CLIENT.put(
        "/tarefas/1",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste",
            "concluido": True,
        },
    )

    CLIENT.put(
        "/tarefas/1",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste",
            "concluido": False,
        },
    )

    metricas = CLIENT.get("/metricas").json()

    assert metricas["quantidade_tarefas_pendentes"] == 1
    assert metricas["quantidade_tarefas_concluidas"] == 0
    assert metricas["quantidade_tarefas_atualizadas"] == 2
    assert metricas["tempo_medio_conclusao_segundos"] == 0


@patch("main.requests.post")
def test_metricas_ao_remover_tarefa_concluida(mock_post):
    criar_tarefa()

    CLIENT.put(
        "/tarefas/1",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste",
            "concluido": True,
        },
    )

    CLIENT.delete("/tarefas/1")

    metricas = CLIENT.get("/metricas").json()

    assert metricas["quantidade_total_tarefas"] == 0
    assert metricas["quantidade_tarefas_pendentes"] == 0
    assert metricas["quantidade_tarefas_concluidas"] == 0
    assert metricas["quantidade_tarefas_removidas"] == 1


@patch("main.requests.post")
def test_tempo_medio_de_conclusao(mock_post):
    criar_tarefa()

    LISTA_TAREFAS[0]["data_criacao"] = (
        datetime.now() - timedelta(seconds=10)
    )

    CLIENT.put(
        "/tarefas/1",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste",
            "concluido": True,
        },
    )

    metricas = CLIENT.get("/metricas").json()

    assert (
        9.9
        <= metricas["tempo_medio_conclusao_segundos"]
        <= 10.1
    )