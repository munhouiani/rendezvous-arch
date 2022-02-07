import datetime
import json
import os
import uuid

from lib.elastic import get_elastic_client
from lib.logging import get_logger
from lib.pulsar import get_client, get_consumer

if __name__ == "__main__":
    pulsar_host = os.getenv("PULSAR_HOST")
    pulsar_port = os.getenv("PULSAR_PORT")
    consumer_topic = os.getenv("CONSUMER_TOPIC")
    elastic_index = os.getenv("ELASTIC_INDEX")
    elastic_host = os.getenv("ELASTIC_HOST")
    elastic_port = os.getenv("ELASTIC_PORT")
    client = get_client(pulsar_host, pulsar_port)
    consumer = get_consumer(
        client, consumer_topic, f"{consumer_topic}-elastic-subscription-{uuid.uuid4()}"
    )
    logger = get_logger(__name__)
    es = get_elastic_client(elastic_host, elastic_port)

    logger.debug(f"pulsar host: {pulsar_host}")
    logger.debug(f"pulsar port: {pulsar_port}")
    logger.debug(f"consumer topic: {consumer_topic}")
    logger.debug(f"elastic index: {elastic_index}")
    logger.debug(f"elastic host: {elastic_host}")
    logger.debug(f"elastic port: {elastic_port}")
    while True:
        msg = consumer.receive()
        data = json.loads(msg.data())
        # fix timestamp
        data["timestamp"] = datetime.datetime.fromtimestamp(
            int(data["timestamp"]), tz=datetime.timezone.utc
        )
        logger.debug(f"Received data {data}")
        res = es.index(index=elastic_index, body=data)
        consumer.acknowledge(msg)
