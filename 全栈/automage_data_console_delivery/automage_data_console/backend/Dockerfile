FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml
COPY automage_agents /app/automage_agents
COPY scripts /app/scripts
COPY configs /app/configs

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi psycopg[binary] SQLAlchemy uvicorn \
    && pip install --no-cache-dir --no-build-isolation -i https://pypi.tuna.tsinghua.edu.cn/simple .

EXPOSE 8000

CMD ["python", "scripts/run_api.py"]
