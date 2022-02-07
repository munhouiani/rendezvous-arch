import datetime
import json
import os
import uuid

import _pulsar
from fastapi import FastAPI
from pydantic import BaseModel

from lib.logging import get_logger
from lib.pulsar import get_client, get_producer, get_consumer

# get ret topic
ret_topic = os.getenv("RET_TOPIC")
producer_topic = os.getenv("PRODUCER_TOPIC")

# connect to pulsar
pulsar_host = os.getenv("PULSAR_HOST")
pulsar_port = os.getenv("PULSAR_PORT")
client = get_client(pulsar_host, pulsar_port)
producer = get_producer(client, producer_topic)
consumer = get_consumer(client, ret_topic, f"scoring-function-{uuid.uuid4()}")

# get timeout seconds
timeout = float(os.getenv("TIMEOUT", 5))

logger = get_logger(__name__)
logger.debug(f"pulsar host: {pulsar_host}")
logger.debug(f"pulsar port: {pulsar_port}")
logger.debug(f"producer topic: {producer_topic}")
logger.debug(f"consumer topic: {ret_topic}")
logger.debug(f"timeout: {timeout}")

app = FastAPI()


class Flower(BaseModel):
    sepalLength: float
    sepalWidth: float
    petalLength: float
    petalWidth: float


@app.get("/ping")
def ping():
    return {"Ping": "Pong"}


def publish_data(data: dict):
    producer.send_async(json.dumps(data).encode("utf-8"), callback=None)
    producer.flush()

    logger.debug(f"Sent data with producer: {data}")


def get_model_result(identifier):
    now = datetime.datetime.utcnow()

    result = {}

    while (datetime.datetime.utcnow() - now) < datetime.timedelta(seconds=timeout):
        try:
            msg = consumer.receive(2)
            data = json.loads(msg.data())
            logger.debug(f"Receive message: {data}")
            consumer.acknowledge(msg)
            if data["messageId"] != identifier:
                continue
            if not result or (
                data["provenance"]["model"]["modelVersion"]
                > result["provenance"]["model"]["modelVersion"]
            ):
                result = data
        except _pulsar.Timeout:
            continue
    model_result = result.get("result", {})
    logger.debug(f"Model result: {model_result}")
    return model_result


@app.post("/predict")
def predict(flower: Flower):
    _id = str(uuid.uuid4())
    message = {
        "timestamp": float(datetime.datetime.now(datetime.timezone.utc).timestamp()),
        "messageId": _id,
        "modelInput": {
            "sepalLength": flower.sepalLength,
            "sepalWidth": flower.sepalWidth,
            "petalLength": flower.petalLength,
            "petalWidth": flower.petalWidth,
        },
        "scoreTopic": ret_topic,
    }

    publish_data(message)
    result = get_model_result(_id)

    message["modelResult"] = result
    message.pop("scoreTopic", None)

    return message
