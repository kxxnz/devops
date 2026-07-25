# API de Tarefas com CI/CD

Projeto desenvolvido por **Joao Pedro Cavalheiro dos Reis** para o curso de DevOps da PUCPR.

A aplicacao fornece uma API REST para cadastro e gerenciamento de tarefas. O projeto tambem possui uma API de notificacoes e um gateway Nginx para centralizar o acesso aos servicos.

## Funcionalidades

- Criar tarefas
- Listar tarefas
- Consultar uma tarefa pelo ID
- Atualizar e concluir tarefas
- Remover tarefas
- Enviar uma notificacao quando uma tarefa for concluida
- Consultar metricas da aplicacao
- Verificar a saude da API

## Arquitetura

O projeto possui tres servicos:

- **Gateway Nginx:** recebe as requisicoes pela porta `8000` e encaminha para as APIs
- **API de tarefas:** executa na porta `8001`
- **API de notificacoes:** executa na porta `8002`

```text
Cliente
   |
   v
Gateway Nginx
   |
   +----> API de Tarefas
   |          |
   |          v
   +----> API de Notificacoes
```

## Tecnologias utilizadas

- Python 3.12
- FastAPI
- Uvicorn
- Requests
- Nginx
- Docker
- Docker Compose
- Kubernetes
- Kind
- GitHub Actions
- Docker Hub
- Pytest
- pytest-cov
- Bandit
- Pylint
- Kubeconform
- FOSSA

## Estrutura do projeto

```text
.
├── .github/workflows/ci_cd.yaml
├── app/
│   ├── main.py
│   └── notificacao.py
├── tests/
│   ├── test_main.py
│   ├── test_metricas.py
│   └── test_notificacao.py
├── deployment.yaml
├── docker-compose.yml
├── Dockerfile
├── nginx.conf
├── requirements.txt
└── setup.sh
```

## Execucao local com Docker Compose

### Pre-requisitos

- Docker
- Docker Compose

### Iniciar o ambiente

```bash
bash setup.sh
```

O script constroi as imagens, inicia os containers e exibe os logs no terminal.

A aplicacao ficara disponivel nos seguintes enderecos:

- Gateway: `http://localhost:8000`
- Swagger pelo gateway: `http://localhost:8000/docs`
- API de tarefas: `http://localhost:8001/docs`
- API de notificacoes: `http://localhost:8002/docs`

Para encerrar, pressione `Ctrl+C` e execute:

```bash
docker compose down
```

## Exemplos de requisicoes

### Criar uma tarefa

```bash
curl -X POST \
  "http://localhost:8000/tarefas?titulo=Estudar&descricao=Revisar%20o%20conteudo"
```

### Listar tarefas

```bash
curl http://localhost:8000/tarefas
```

### Consultar uma tarefa

```bash
curl http://localhost:8000/tarefas/1
```

### Atualizar e concluir uma tarefa

```bash
curl -X PUT \
  "http://localhost:8000/tarefas/1?titulo=Estudar&descricao=Conteudo%20revisado&concluido=true"
```

### Remover uma tarefa

```bash
curl -X DELETE http://localhost:8000/tarefas/1
```

### Consultar metricas

```bash
curl http://localhost:8000/metricas
```

### Verificar a saude da API

```bash
curl http://localhost:8000/health
```

## Execucao dos testes

Instale as dependencias da aplicacao e as ferramentas de desenvolvimento:

```bash
pip install -r requirements.txt
pip install pytest httpx pytest-cov bandit pylint
```

Execute os testes:

```bash
PYTHONPATH=app pytest -v
```

Execute os testes com cobertura minima de 80%:

```bash
PYTHONPATH=app pytest \
  --cov=app \
  --cov-report=term-missing \
  --cov-fail-under=80
```

## Analise de codigo

### Bandit

```bash
bandit -r app/
```

### Pylint

```bash
pylint app/ || true
```

## Execucao no Kubernetes

### Pre-requisitos

- Docker
- kubectl
- Kind

Crie um cluster local:

```bash
kind create cluster \
  --name devops-deploy \
  --wait 120s
```

Aplique os manifestos:

```bash
kubectl apply -f deployment.yaml
```

Aguarde os Deployments:

```bash
kubectl rollout status deployment/tarefas --timeout=180s
kubectl rollout status deployment/notificacao --timeout=180s
kubectl rollout status deployment/gateway --timeout=180s
```

Confira os recursos:

```bash
kubectl get deployments
kubectl get pods
kubectl get services
```

Disponibilize o gateway localmente:

```bash
kubectl port-forward service/gateway 8080:80
```

Acesse:

- Gateway: `http://localhost:8080`
- Swagger: `http://localhost:8080/docs`

Para remover o cluster:

```bash
kind delete cluster --name devops-deploy
```

## Pipeline CI/CD

A pipeline esta configurada em `.github/workflows/ci_cd.yaml` e executa as seguintes etapas:

1. Instalacao das dependencias
2. Testes automatizados
3. Verificacao de cobertura minima de 80%
4. Analise de seguranca com Bandit
5. Analise de codigo com Pylint
6. Validacao do Docker Compose
7. Build da imagem Docker
8. Validacao dos manifestos com Kubeconform
9. Teste da aplicacao em um cluster Kind
10. Analise de dependencias e licencas com FOSSA
11. Publicacao da imagem no Docker Hub
12. Implantacao no Kubernetes com runner self-hosted

A integracao continua e executada automaticamente em Pull Requests para a branch `main`.

A entrega e a implantacao sao executadas depois que as alteracoes sao integradas na branch `main`.

## Imagem Docker

A imagem da aplicacao esta publicada em:

```text
jpwrlld/devops-api
```

Para baixar a versao mais recente:

```bash
docker pull jpwrlld/devops-api:latest
```

## Repositorio

```text
https://github.com/kxxnz/devops
```