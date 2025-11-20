FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY src/ /app/src/

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-editable

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8501

CMD ["streamlit", "run", "/app/src/digital_shelf/app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Fpr prod later
# FROM python:3.12-slim
# WORKDIR /app
# COPY --from=builder /app/.venv /app/.venv
# COPY src/digital_shelf/app /app/app
# CMD ["/app/.venv/bin/streamlit", "run", "/app/app/app.py"]