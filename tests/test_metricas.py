from fastapi.testclient import TestClient

from app import APP

CLIENT = TestClient(APP)

def criar_tarefa_mock():
    requisicao = CLIENT.post("/tarefas?id=0&titulo=tarefa&descricao=descricao-tarefa")


def test_qtde_tarefas():
    criar_tarefa_mock()

    requisicao = CLIENT.get("/metricas").json()

    assert requisicao['qtde_tarefas'] == 1
    

def test_qtde_tarefas_concluidas():
    CLIENT.put("/tarefas/0?concluido=true")

    requisicao = CLIENT.get("/metricas").json()

    assert requisicao['qtde_tarefas_concluidas'] == 1
    assert requisicao['qtde_tarefas_pendentes'] == 0
    assert requisicao['qtde_tarefas_atualizadas'] == 2


def test_apagar_tarefa():
    CLIENT.delete("/tarefas/0")

    requisicao = CLIENT.get("/metricas").json()

    assert requisicao['qtde_tarefas_removidas'] == 3
    assert requisicao['qtde_tarefas'] == 0
