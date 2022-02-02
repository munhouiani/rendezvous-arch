import datetime
import gzip
import json
import os
import uuid

from lib.pulsar import get_client, get_consumer

if __name__ == "__main__":
    pulsar_host = os.getenv("PULSAR_HOST")
    pulsar_port = os.getenv("PULSAR_PORT")
    log_topic = os.getenv("LOG_TOPIC")
    timeout = float(os.getenv("TIMEOUT"))
    output_path = os.getenv("OUTPUT_DIR")
    threshold = int(os.getenv("THRESHOLD"))
    client = get_client(pulsar_host, pulsar_port)
    consumer = get_consumer(
        client, log_topic, f"{log_topic}-collector-subscription-{uuid.uuid4()}"
    )

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
            with gzip.open(filepath, "wb") as f_out:
                for log in logs:
                    log = json.loads(log)
                    f_out.write(f"{json.dumps(log)}\n".encode("utf-8"))
                logs.clear()
        try:
            msg = consumer.receive(2)
            data = msg.data()
            logs.append(data)
            consumer.acknowledge(msg)
        except:
            continue

    client.close()
