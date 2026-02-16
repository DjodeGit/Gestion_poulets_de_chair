FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
#LIGNE MAGIQUE – MIRROR OFFICIEL + TIMEOUT ÉNORME
RUN pip install --no-cache-dir --timeout=2000 --retries=20 -i https://pypi.org/simple/ -r requirements.txt
COPY . .
# Port utilisé par Render
EXPOSE 10000

# ✅ COMMANDE DE DÉMARRAGE EN PRODUCTION
CMD ["gunicorn", "gestion_poulets.wsgi:application", "--bind", "0.0.0.0:10000"]