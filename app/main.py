import os
from datetime import datetime

import requests
from fastapi import FastAPI

LISTA_TAREFAS = []
APP = FastAPI()


def nova_tarefa(id: int, titulo: str, descricao: str):
    return {
        "id": id,
        "titulo": titulo,
        "descricao": descricao,
        "concluido": False,
        "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),        
    }

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
    return {"message": "Bem-vindo à API de Tarefas!"}


@APP.get("/tarefas")
def listar_tarefas():
    # lista tarefas somente com id e titulo
    if len(LISTA_TAREFAS) == 0:
        return {"message": "Nenhuma tarefa encontrada."}
        
    tarefas = []

    for tarefa in LISTA_TAREFAS:
        info = {"id": tarefa["id"], "titulo": tarefa["titulo"]}
        tarefas.append(info)

    return tarefas


@APP.get("/tarefas/{id}")
def listar_tarefa_especifica(id: int):
    for tarefa in LISTA_TAREFAS:
        if tarefa["id"] == id:
            return tarefa

    if len(LISTA_TAREFAS) == 0:
        return {"message": "Nenhuma tarefa encontrada."}

    return {"message": "Tarefa não encontrada."}


@APP.post("/tarefas")
def criar_tarefa(titulo: str, descricao: str):
    titulo = titulo.strip()
    descricao = descricao.strip()

    if titulo == "":
        return {"message": "O título da tarefa não pode ser vazio."}

    for tarefa in LISTA_TAREFAS:
        if tarefa["titulo"] == titulo:
            return {"message": "Já existe uma tarefa com esse título."}

    tarefa = nova_tarefa(proximo_id(), titulo, descricao)

    LISTA_TAREFAS.append(tarefa)

    return {"message": "Tarefa criada com sucesso."}


@APP.put("/tarefas/{id}")
def atualizar_tarefa_especifica(id: int, titulo: str, descricao: str, concluido: bool):
    titulo = titulo.strip()
    descricao = descricao.strip()

    if titulo == "":
        return {"message": "O título da tarefa não pode ser vazio."}

    for tarefa in LISTA_TAREFAS:
        if tarefa["id"] == id:
            tarefa["titulo"] = titulo
            tarefa["descricao"] = descricao
            tarefa["concluido"] = concluido

            

            return {"message": "Tarefa atualizada com sucesso."}

    return {"message": "Tarefa não encontrada."}

@APP.delete("/tarefas/{id}")
def deletar_tarefa_especifica(id: int):
    for tarefa in LISTA_TAREFAS:
        if tarefa["id"] == id:
            LISTA_TAREFAS.remove(tarefa)
            return {"message": "Tarefa deletada com sucesso."}

    return {"message": "Tarefa não encontrada."}
