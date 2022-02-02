import os
import uuid

from lib.pulsar import get_client, get_consumer, get_producer

if __name__ == "__main__":
    pulsar_host = os.getenv("PULSAR_HOST")
    pulsar_port = os.getenv("PULSAR_PORT")
    model_name = os.getenv("MODEL_NAME")
    client = get_client(pulsar_host, pulsar_port)
    consumer = get_consumer(client, "iris", f"{model_name}-subscription-{uuid.uuid4()}")
    producer = get_producer(client, "log")

    while True:
        msg = consumer.receive()
        data = msg.data()
        producer.send(data)
        consumer.acknowledge(msg)

    client.close()
