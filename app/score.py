import datetime
import json
import os
import uuid

from fastapi import FastAPI
from pydantic import BaseModel

from lib.pulsar import get_client, get_producer, get_consumer

# get ret topic
ret_topic = os.getenv("RET_TOPIC")

# connect to pulsar
pulsar_host = os.getenv("PULSAR_HOST")
pulsar_port = os.getenv("PULSAR_PORT")
client = get_client(pulsar_host, pulsar_port)
producer = get_producer(client, "iris")
consumer = get_consumer(client, ret_topic, f"scoring-function-{uuid.uuid4()}")

# get timeout seconds
timeout = float(os.getenv("TIMEOUT", 5))
app = FastAPI()


class Flower(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


@app.get("/ping")
def ping():
    return {"Ping": "Pong"}


def publish_data(data: dict):
    producer.send_async(json.dumps(data).encode("utf-8"), callback=None)
    producer.flush()


def get_model_result(identifier):
    now = datetime.datetime.utcnow()

    model_result = {}

    while (datetime.datetime.utcnow() - now) < datetime.timedelta(seconds=timeout):
        try:
            msg = consumer.receive(0.1)
            data = json.loads(msg.data())
            consumer.acknowledge(msg)
            if data["messageId"] != identifier:
                continue
            if not model_result or (
                data["provenance"]["model"]["modelVersion"]
                > model_result["provenance"]["model"]["modelVersion"]
            ):
                model_result = data
        except:
            continue

    model_result = model_result.get("result", {}).get("result", None)
    if model_result:
        model_result = model_result[0]
    return model_result


@app.post("/predict")
def predict(flower: Flower):
    _id = str(uuid.uuid4())
    message = {
        "timestamp": float(datetime.datetime.now(datetime.timezone.utc).timestamp()),
        "messageId": _id,
        "modelInput": {
            "sepalLength": flower.sepal_length,
            "sepalWidth": flower.sepal_width,
            "petalLength": flower.petal_length,
            "petalWidth": flower.petal_width,
        },
        "scoreTopic": ret_topic,
    }

    publish_data(message)
    result = get_model_result(_id)

    message["modelResult"] = result
    message.pop("scoreTopic", None)

    return message
