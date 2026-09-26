FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear directorios y dar permisos completos (777)
RUN mkdir -p /app/data /app/uploads && chmod -R 777 /app/data /app/uploads

EXPOSE 5000

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]
