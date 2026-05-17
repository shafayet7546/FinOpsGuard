FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

# Pull latest Debian security patches into the runtime layer.
RUN apt-get update \
	&& apt-get upgrade -y \
	&& rm -rf /var/lib/apt/lists/*

# Run as non-root user for security (OWASP container best practice)
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy dependencies into a standard runtime location.
COPY --from=builder /install /usr/local

COPY /app ./app/
COPY /assets ./assets/

# Create a writable location for SQLite when running as non-root.
RUN mkdir -p /app/data && chown -R appuser:appgroup /app/data

ENV DATABASE_URL=sqlite:////app/data/finopsguard.db
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]