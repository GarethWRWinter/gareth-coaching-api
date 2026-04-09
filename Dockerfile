FROM python:3.12-slim

WORKDIR /app

# Install system deps for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head 2>&1; echo 'Migrations complete, starting server on port ${PORT:-8000}'; exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info"]
