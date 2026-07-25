from fastapi.testclient import TestClient

from main import APP, LISTA_TAREFAS

CLIENT = TestClient(APP)


def setup_function():
    LISTA_TAREFAS.clear()


def test_index():
    response = CLIENT.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Bem-vindo à API de Tarefas!"
    }


def test_criar_tarefa():
    response = CLIENT.post(
        "/tarefas",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste"
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Tarefa criada com sucesso."
    }


def test_nao_permitir_tarefa_duplicada():
    CLIENT.post(
        "/tarefas",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste"
        }
    )

    response = CLIENT.post(
        "/tarefas",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste"
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Já existe uma tarefa com esse título."
    }


def test_listar_tarefa():
    CLIENT.post(
        "/tarefas",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste"
        }
    )

    response = CLIENT.get("/tarefas/1")

    assert response.status_code == 200

    dados = response.json()

    assert dados["id"] == 1
    assert dados["titulo"] == "tarefa teste"
    assert dados["descricao"] == "descricao teste"
    assert dados["concluido"] is False


def test_atualizar_tarefa():
    CLIENT.post(
        "/tarefas",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste"
        }
    )

    response = CLIENT.put(
        "/tarefas/1",
        params={
            "titulo": "nova tarefa",
            "descricao": "nova descricao",
            "concluido": True
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Tarefa atualizada com sucesso."
    }

    tarefa = CLIENT.get("/tarefas/1")

    assert tarefa.json()["titulo"] == "nova tarefa"
    assert tarefa.json()["concluido"] is True


def test_deletar_tarefa():
    CLIENT.post(
        "/tarefas",
        params={
            "titulo": "tarefa teste",
            "descricao": "descricao teste"
        }
    )

    response = CLIENT.delete("/tarefas/1")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Tarefa deletada com sucesso."
    }


def test_deletar_tarefa_inexistente():
    response = CLIENT.delete("/tarefas/999")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Tarefa não encontrada."
    }