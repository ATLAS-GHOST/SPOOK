FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir prometheus_client

EXPOSE 9000/udp
EXPOSE 8000

CMD ["python", "receiver_v2.py"]