import datetime
import json
import os
import pickle
import uuid

from lib.logging import get_logger
from lib.pulsar import get_client, get_consumer, get_producer

logger = get_logger(__name__)


def load_model():
    model_path = os.getenv("MODEL_PATH")
    model = pickle.load(open(model_path, "rb"))
    logger.debug(f"model loaded from: {model_path}")

    return model


def get_model_result(model, data):
    model_input = data["modelInput"]
    features = [
        [
            model_input["sepalLength"],
            model_input["sepalWidth"],
            model_input["petalLength"],
            model_input["petalWidth"],
        ]
    ]

    result = model.predict(features).tolist()[0]
    logger.debug(f"Predict {features}, result: {result}")

    return result


if __name__ == "__main__":
    pulsar_host = os.getenv("PULSAR_HOST")
    pulsar_port = os.getenv("PULSAR_PORT")
    model_name = os.getenv("MODEL_NAME")
    model_version = int(os.getenv("MODEL_VERSION", 0))
    consumer_topic = os.getenv("CONSUMER_TOPIC")
    client = get_client(pulsar_host, pulsar_port)
    consumer = get_consumer(
        client, consumer_topic, f"{model_name}-subscription-{uuid.uuid4()}"
    )

    logger.debug(f"pulsar host: {pulsar_host}")
    logger.debug(f"pulsar port: {pulsar_port}")
    logger.debug(f"consumer topic: {consumer_topic}")
    logger.debug(f"model: {model_name}")
    logger.debug(f"model version: {model_version}")

    model = load_model()

    while True:
        msg = consumer.receive()
        data = json.loads(msg.data())
        logger.debug(f"Receive message: {data}")

        # get ret addr
        ret_topic = data["scoreTopic"]
        producer = get_producer(client, ret_topic)
        logger.debug(f"Create a producer for topic {ret_topic}")

        result = get_model_result(model, data)
        request_timestamp = datetime.datetime.fromtimestamp(
            float(data["timestamp"]), datetime.timezone.utc
        )
        now_timestamp = datetime.datetime.now(datetime.timezone.utc)
        time_after_request = (now_timestamp - request_timestamp).total_seconds() * 1000

        data["result"] = {
            "modelName": model_name,
            "result": result,
        }

        if "provenance" not in data:
            data["provenance"] = {}

        data["provenance"]["model"] = {
            "modelName": model_name,
            "elapsedTimeAfterRequest": time_after_request,
            "modelVersion": model_version,
        }

        producer.send(json.dumps(data).encode("utf-8"))
        producer.flush()
        producer.close()
        logger.debug(f"Sent data with producer: {data}")

        consumer.acknowledge(msg)
