# Build stage
FROM python:3.14-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Set work directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    pkg-config libcairo2-dev libpango1.0-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /uvx /bin/

# Install Python dependencies (cached unless pyproject.toml/uv.lock change)
COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-dev --extra prod

# Runtime stage
FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Set work directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    postgresql-client \
    # weasyprint dependencies
    libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 \
    locales \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i '/pt_BR.UTF-8/s/^# //g' /etc/locale.gen && \
  locale-gen pt_BR.UTF-8 && \
  update-locale LANG=pt_BR.UTF-8

# Copy the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy project
COPY . /app/

# Create socket directory
RUN mkdir -p /run/sockets

# Create staticfiles directory for collected static
RUN mkdir -p /app/staticfiles

# Create media directory
RUN mkdir -p /app/media

# Set permissions
RUN chmod -R 755 /app/staticfiles /app/media

# Copy entrypoint script
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
