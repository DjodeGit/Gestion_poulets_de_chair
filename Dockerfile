FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
#LIGNE MAGIQUE – MIRROR OFFICIEL + TIMEOUT ÉNORME
RUN pip install --no-cache-dir --timeout=2000 --retries=20 -i https://pypi.org/simple/ -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]