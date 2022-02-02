import _pulsar
import pulsar
import socket


def get_client(pulsar_host: str, pulsar_port: str):
    try:
        # health check
        s = socket.socket()
        s.connect((pulsar_host, int(pulsar_port)))
        client = pulsar.Client(f"pulsar://{pulsar_host}:{pulsar_port}")
        s.close()
        return client
    except (_pulsar.ConnectError, _pulsar.Timeout, OSError):
        exit(1)


def get_producer(client, topic: str):
    try:
        producer = client.create_producer(topic)
        return producer
    except (_pulsar.ConnectError, _pulsar.Timeout):
        client.close()
        exit(1)


def get_consumer(client, topic: str, subscription_name: str):
    try:
        consumer = client.subscribe(topic, subscription_name=subscription_name)
        return consumer
    except (_pulsar.ConnectError, _pulsar.Timeout):
        client.close()
        exit(1)
