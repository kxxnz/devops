import logging
import os
from datetime import datetime

import requests
from fastapi import FastAPI, HTTPException

LISTA_TAREFAS = []
APP = FastAPI()

URL_NOTIFICACAO = os.getenv(
    "URL_NOTIFICACAO",
    "http://127.0.0.1:8002/notificacao",
)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

if LOG_LEVEL == "DEBUG":
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO

LOGGER = logging.getLogger("DevOps")
LOGGER.setLevel(LOG_LEVEL)

FORMATADOR = logging.Formatter(
    "%(name)s | %(asctime)s | %(levelname)s | %(message)s"
)

# Evita duplicar logs quando o Uvicorn estiver usando --reload.
if not LOGGER.handlers:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(FORMATADOR)
    LOGGER.addHandler(stream_handler)


METRICAS = {
    "quantidade_total_tarefas": 0,
    "quantidade_tarefas_pendentes": 0,
    "quantidade_tarefas_concluidas": 0,
    "quantidade_tarefas_atualizadas": 0,
    "quantidade_tarefas_removidas": 0,
    "tempo_medio_conclusao_segundos": 0,
}


def nova_tarefa(id: int, titulo: str, descricao: str):
    tarefa = {
        "id": id,
        "titulo": titulo,
        "descricao": descricao,
        "concluido": False,
        "data_criacao": datetime.now(),
        "data_conclusao": None,
    }

    LOGGER.debug(f"Criando tarefa: {tarefa}")

    return tarefa


def proximo_id():
    if len(LISTA_TAREFAS) == 0:
        return 1

    maior_id = 0

    for tarefa in LISTA_TAREFAS:
        if tarefa["id"] > maior_id:
            maior_id = tarefa["id"]

    return maior_id + 1


@APP.get("/")
def index():
    LOGGER.info("Rota GET '/' acessada.")

    return {"message": "Bem-vindo à API de Tarefas!"}


@APP.get("/tarefas")
def listar_tarefas():
    LOGGER.info("Rota GET '/tarefas' acessada.")

    if len(LISTA_TAREFAS) == 0:
        return {"message": "Nenhuma tarefa encontrada."}

    tarefas = []

    for tarefa in LISTA_TAREFAS:
        info = {
            "id": tarefa["id"],
            "titulo": tarefa["titulo"],
        }

        tarefas.append(info)

    return tarefas


@APP.get("/tarefas/{id}")
def listar_tarefa_especifica(id: int):
    LOGGER.info(f"Rota GET '/tarefas/{id}' acessada.")

    for tarefa in LISTA_TAREFAS:
        if tarefa["id"] == id:
            return tarefa

    LOGGER.error(f"Tarefa de ID {id} não encontrada.")

    raise HTTPException(
        status_code=404,
        detail={"message": "Tarefa não encontrada."},
    )


@APP.post("/tarefas", status_code=201)
def criar_tarefa(titulo: str, descricao: str):
    titulo = titulo.strip()
    descricao = descricao.strip()

    if titulo == "":
        LOGGER.error("Tentativa de criar tarefa sem título.")

        raise HTTPException(
            status_code=400,
            detail={
                "message": "O título da tarefa não pode ser vazio."
            },
        )

    for tarefa in LISTA_TAREFAS:
        if tarefa["titulo"].lower() == titulo.lower():
            LOGGER.error(
                f"Já existe uma tarefa com o título '{titulo}'."
            )

            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Já existe uma tarefa com esse título."
                },
            )

    tarefa = nova_tarefa(
        proximo_id(),
        titulo,
        descricao,
    )

    LISTA_TAREFAS.append(tarefa)

    METRICAS["quantidade_total_tarefas"] += 1
    METRICAS["quantidade_tarefas_pendentes"] += 1

    LOGGER.info(
        f"Rota POST '/tarefas' acessada. "
        f"Tarefa de ID {tarefa['id']} criada."
    )

    return {
        "message": "Tarefa criada com sucesso.",
        "id": tarefa["id"],
    }


@APP.put("/tarefas/{id}")
def atualizar_tarefa_especifica(
    id: int,
    titulo: str,
    descricao: str,
    concluido: bool,
):
    titulo = titulo.strip()
    descricao = descricao.strip()

    if titulo == "":
        raise HTTPException(
            status_code=400,
            detail={
                "message": "O título da tarefa não pode ser vazio."
            },
        )

    for tarefa in LISTA_TAREFAS:
        if tarefa["id"] == id:
            estava_concluida = tarefa["concluido"]

            tarefa["titulo"] = titulo
            tarefa["descricao"] = descricao
            tarefa["concluido"] = concluido

            # A tarefa acabou de passar de pendente para concluída.
            if concluido is True and estava_concluida is False:
                data_finalizacao = datetime.now()

                tarefa["data_conclusao"] = data_finalizacao

                METRICAS["quantidade_tarefas_concluidas"] += 1
                METRICAS["quantidade_tarefas_pendentes"] -= 1

                try:
                    requests.post(
                        URL_NOTIFICACAO,
                        params={
                            "titulo": titulo,
                            "data_finalizacao": (
                                data_finalizacao.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            ),
                        },
                        timeout=5,
                    )

                    LOGGER.info(
                        f"Notificação da tarefa de ID {id} enviada."
                    )

                except requests.RequestException as erro:
                    LOGGER.error(
                        f"Erro ao enviar notificação: {erro}"
                    )

            # A tarefa era concluída e voltou a ser pendente.
            if concluido is False and estava_concluida is True:
                tarefa["data_conclusao"] = None

                METRICAS["quantidade_tarefas_concluidas"] -= 1
                METRICAS["quantidade_tarefas_pendentes"] += 1

            METRICAS["quantidade_tarefas_atualizadas"] += 1

            LOGGER.info(
                f"Rota PUT '/tarefas/{id}' acessada. "
                f"Tarefa atualizada."
            )

            return {
                "message": "Tarefa atualizada com sucesso."
            }

    LOGGER.error(
        f"Não foi possível atualizar. "
        f"Tarefa de ID {id} não encontrada."
    )

    raise HTTPException(
        status_code=404,
        detail={"message": "Tarefa não encontrada."},
    )


@APP.delete("/tarefas/{id}")
def deletar_tarefa_especifica(id: int):
    for tarefa in LISTA_TAREFAS:
        if tarefa["id"] == id:
            LISTA_TAREFAS.remove(tarefa)

            METRICAS["quantidade_total_tarefas"] -= 1
            METRICAS["quantidade_tarefas_removidas"] += 1

            if tarefa["concluido"] is True:
                METRICAS["quantidade_tarefas_concluidas"] -= 1
            else:
                METRICAS["quantidade_tarefas_pendentes"] -= 1

            LOGGER.info(
                f"Rota DELETE '/tarefas/{id}' acessada. "
                f"Tarefa removida."
            )

            return {
                "message": "Tarefa deletada com sucesso."
            }

    LOGGER.error(
        f"Não foi possível excluir. "
        f"Tarefa de ID {id} não encontrada."
    )

    raise HTTPException(
        status_code=404,
        detail={"message": "Tarefa não encontrada."},
    )


@APP.get("/metricas")
def listar_metricas():
    tempo_total = 0
    quantidade_com_tempo = 0

    for tarefa in LISTA_TAREFAS:
        if (
            tarefa["concluido"] is True
            and tarefa["data_conclusao"] is not None
        ):
            diferenca = (
                tarefa["data_conclusao"]
                - tarefa["data_criacao"]
            )

            tempo_total += diferenca.total_seconds()
            quantidade_com_tempo += 1

    if quantidade_com_tempo > 0:
        METRICAS["tempo_medio_conclusao_segundos"] = round(
            tempo_total / quantidade_com_tempo,
            2,
        )
    else:
        METRICAS["tempo_medio_conclusao_segundos"] = 0

    LOGGER.info("Rota GET '/metricas' acessada.")

    return METRICAS


@APP.get("/health")
def health():
    LOGGER.info("Rota GET '/health' acessada.")

    return {"message": "healthy"}