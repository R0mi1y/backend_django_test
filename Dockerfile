FROM python:3.11-slim

# Impede o Python de gerar arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1

# Impede que o Python seja bufferizado
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]