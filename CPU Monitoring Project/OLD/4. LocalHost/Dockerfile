FROM python:3.12-slim

WORKDIR /udp_testing

COPY . .

RUN pip install --no-cache-dir prometheus_client psutil

EXPOSE 9000/udp
EXPOSE 8000

CMD ["python", "receiver.py"]