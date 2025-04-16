FROM python:3.9-slim

WORKDIR /app

RUN pip install requests flask dotenv pika schedule

COPY . .

CMD ["python", "-u", "main.py"]