FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY app ./app
RUN pip install --no-cache-dir .

ENV INV_PORT=8091
EXPOSE 8091
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${INV_PORT}"]
