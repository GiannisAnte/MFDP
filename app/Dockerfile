FROM python:3.11-slim

WORKDIR /app

# COPY requirements.txt ./requirements.txt
COPY requirements.txt ./requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app/ ./

EXPOSE 8080

CMD ["python", "main.py"]
# FROM python:3.11-slim

# WORKDIR /app

# # Устанавливаем netcat для проверки портов, скачиваем wait-for-it.sh
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends netcat-openbsd curl && \
#     curl -sSL https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
#          -o /usr/local/bin/wait-for-it.sh && \
#     chmod +x /usr/local/bin/wait-for-it.sh && \
#     apt-get purge -y --auto-remove curl && \
#     rm -rf /var/lib/apt/lists/*


# COPY requirements.txt .
# RUN pip install --upgrade pip && pip install -r requirements.txt


# COPY . .

# EXPOSE 8080

# # Сначала ждём RabbitMQ, затем запускаем Uvicorn
# CMD ["/usr/local/bin/wait-for-it.sh", "rabbitmq:5672", "--", \
#      "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
