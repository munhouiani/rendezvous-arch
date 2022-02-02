FROM --platform=linux/amd64 python:3.9.10

# update pip
RUN /usr/local/bin/python -m pip install --upgrade pip

# install model dependencies
RUN pip install "pulsar-client==2.9.1"

# set environment variables
ARG PULSAR_HOST
ARG PULSAR_PORT
ARG TIMEOUT
ARG THRESHOLD
ARG LOG_TOPIC
ARG OUTPUT_DIR
ENV PULSAR_HOST=${PULSAR_HOST}
ENV PULSAR_PORT=${PULSAR_PORT}
ENV TIMEOUT=${TIMEOUT}
ENV THRESHOLD=${THRESHOLD}
ENV LOG_TOPIC=${LOG_TOPIC}
ENV OUTPUT_DIR=${OUTPUT_DIR}

# copy lib
COPY ../lib /lib

# copy app
COPY ../app/log_collector.py /log_collector.py

# run
ENTRYPOINT ["python", "/log_collector.py"]
