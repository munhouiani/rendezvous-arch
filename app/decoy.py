import os
import uuid

from lib.pulsar import get_client, get_consumer, get_producer
from lib.logging import get_logger

if __name__ == "__main__":
    pulsar_host = os.getenv("PULSAR_HOST")
    pulsar_port = os.getenv("PULSAR_PORT")
    model_name = os.getenv("MODEL_NAME")
    producer_topic = os.getenv("PRODUCER_TOPIC")
    consumer_topic = os.getenv("CONSUMER_TOPIC")
    client = get_client(pulsar_host, pulsar_port)
    consumer = get_consumer(
        client, consumer_topic, f"{model_name}-subscription-{uuid.uuid4()}"
    )
    producer = get_producer(client, producer_topic)

    logger = get_logger(__name__)
    logger.debug(f"pulsar host: {pulsar_host}")
    logger.debug(f"pulsar port: {pulsar_port}")
    logger.debug(f"producer topic: {producer_topic}")
    logger.debug(f"consumer topic: {consumer_topic}")
    logger.debug(f"model: {model_name}")

    while True:
        msg = consumer.receive()
        data = msg.data()
        logger.debug(f"Receive message: {data}")
        producer.send(data)
        logger.debug(f"Sent data with producer: {data}")
        consumer.acknowledge(msg)
