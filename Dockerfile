FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código
COPY backend/ /app/backend/
# Copiamos los datos de efemérides (necesario para asteroides como Quirón)
COPY se_data/ /app/se_data/

ENV DJANGO_SECRET_KEY=dev DJANGO_DEBUG=False SE_EPHE_PATH=/app/se_data
EXPOSE 8000

CMD ["python", "backend/manage.py", "runserver", "0.0.0.0:8000"]