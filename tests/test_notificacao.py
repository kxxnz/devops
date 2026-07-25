from fastapi.testclient import TestClient

from notificacao import APP

CLIENT = TestClient(APP)


def test_index():
    resposta = CLIENT.get("/")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "message": "Bem-vindo à API de Notificações!"
    }


def test_enviar_notificacao(capsys):
    resposta = CLIENT.post(
        "/notificacao",
        params={
            "titulo": "tarefa teste",
            "data_finalizacao": "2026-07-25 10:00:00",
        },
    )

    saida = capsys.readouterr().out

    assert resposta.status_code == 200
    assert resposta.json() == {
        "message": "Notificação enviada com sucesso!"
    }
    assert "[ NOTIFICAÇÃO DE TAREFA FINALIZADA ]" in saida
    assert "Tarefa: tarefa teste" in saida
    assert "Finalizada em: 2026-07-25 10:00:00" in saida
    assert "[ NOTIFICAÇÃO ENVIADA COM SUCESSO! ]" in saida


def test_notificacao_sem_titulo():
    resposta = CLIENT.post(
        "/notificacao",
        params={
            "data_finalizacao": "2026-07-25 10:00:00",
        },
    )

    assert resposta.status_code == 422


def test_notificacao_sem_data_finalizacao():
    resposta = CLIENT.post(
        "/notificacao",
        params={
            "titulo": "tarefa teste",
        },
    )

    assert resposta.status_code == 422