FROM python:3.12-slim-bullseye

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /uvx /bin/

# Copy the project into the image
COPY . /home/fastapi

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /home/fastapi
RUN uv sync --frozen --no-cache

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]