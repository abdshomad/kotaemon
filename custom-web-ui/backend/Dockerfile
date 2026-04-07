FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/libs

WORKDIR /app

COPY custom-web-ui/backend/requirements.txt /app/custom-web-ui/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/custom-web-ui/backend/requirements.txt

COPY libs /app/libs
COPY custom-web-ui/backend /app/custom-web-ui/backend

WORKDIR /app/custom-web-ui/backend
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
