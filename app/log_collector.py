import datetime
import gzip
import json
import os
import uuid

from lib.logging import get_logger
from lib.pulsar import get_client, get_consumer

if __name__ == "__main__":
    pulsar_host = os.getenv("PULSAR_HOST")
    pulsar_port = os.getenv("PULSAR_PORT")
    consumer_topic = os.getenv("CONSUMER_TOPIC")
    timeout = float(os.getenv("TIMEOUT"))
    output_path = os.getenv("OUTPUT_DIR")
    threshold = int(os.getenv("THRESHOLD"))
    client = get_client(pulsar_host, pulsar_port)
    consumer = get_consumer(
        client,
        consumer_topic,
        f"{consumer_topic}-collector-subscription-{uuid.uuid4()}",
    )
    logger = get_logger(__name__)

    logger.debug(f"pulsar host: {pulsar_host}")
    logger.debug(f"pulsar port: {pulsar_port}")
    logger.debug(f"consumer topic: {consumer_topic}")
    logger.debug(f"timeout: {timeout}")
    logger.debug(f"output path: {output_path}")
    logger.debug(f"threshold: {threshold}")
    logs = []
    now = datetime.datetime.utcnow()
    timeout = datetime.timedelta(seconds=timeout)
    # collect when timeout or logs reach #threshold message
    while True:
        time_diff = datetime.datetime.utcnow() - now
        is_timeout = time_diff > timeout
        if len(logs) >= threshold or is_timeout:
            if is_timeout:
                now = datetime.datetime.utcnow()
            if not logs:
                continue

            filename = f"log-{uuid.uuid4()}.gz"
            filepath = os.path.join(output_path, filename)
            logger.debug(
                f"output log to {filepath} timeout: {is_timeout}, length: {len(logs)}"
            )
            with gzip.open(filepath, "wb") as f_out:
                for log in logs:
                    log = json.loads(log)
                    f_out.write(f"{json.dumps(log)}\n".encode("utf-8"))
                logs.clear()
        try:
            msg = consumer.receive(2)
            data = msg.data()
            logger.debug(f"Received data {data}")
            logs.append(data)
            consumer.acknowledge(msg)
        except:
            continue

    client.close()
