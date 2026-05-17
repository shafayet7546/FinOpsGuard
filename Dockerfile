FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

# Run as non-root user for security (OWASP container best practice)
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy dependencies into a standard runtime location.
COPY --from=builder /install /usr/local

COPY /app ./app/
COPY /assets ./assets/

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]