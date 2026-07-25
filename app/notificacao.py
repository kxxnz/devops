from datetime import datetime
from fastapi import FastAPI

APP = FastAPI()

def formatar_data_log():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def imprimir_log_notificacao(titulo: str, data_finalizacao: str):
    data_recebimento = formatar_data_log()

    print(f"""
    [ NOTIFICAÇÃO DE TAREFA FINALIZADA ]

    - Tarefa: {titulo}
    - Finalizada em: {data_finalizacao}
    - Notificação recebida em: {data_recebimento}

    [ NOTIFICAÇÃO ENVIADA COM SUCESSO! ]
    """)

@APP.get("/")
def index():
    return {"message": "Bem-vindo à API de Notificações!"}

@APP.post("/notificacao")
def enviar_notificacao(titulo: str, data_finalizacao: str):
    imprimir_log_notificacao(titulo, data_finalizacao)
    return {"message": "Notificação enviada com sucesso!"}