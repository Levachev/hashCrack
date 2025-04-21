FROM python:3.9-slim

WORKDIR /app

RUN pip install requests flask dotenv pika pymongo=='4.11.3' schedule

COPY . .

CMD ["python", "-u", "main.py"]