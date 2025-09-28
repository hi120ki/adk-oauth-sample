FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock .

RUN uv sync --frozen --no-cache

COPY app .

ENV PORT=8000

CMD ["/app/.venv/bin/python", "main.py"]
