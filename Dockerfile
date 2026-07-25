FROM public.ecr.aws/docker/library/python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    --trusted-host pypi.python.org \
    -r requirements.txt

COPY app/ .

CMD ["python", "-m", "uvicorn", "main:APP", "--host", "0.0.0.0", "--port", "8001"]