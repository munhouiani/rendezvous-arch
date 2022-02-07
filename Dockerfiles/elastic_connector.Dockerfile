FROM --platform=linux/amd64 python:3.9.10

# update pip
RUN /usr/local/bin/python -m pip install --upgrade pip

# install model dependencies
RUN pip install "pulsar-client==2.9.1" "elasticsearch==7.13.3"

# set environment variables
ARG PULSAR_HOST
ARG PULSAR_PORT
ARG CONSUMER_TOPIC
ARG ELASTIC_INDEX
ARG ELASTIC_HOST
ARG ELASTIC_PORT
ENV PULSAR_HOST=${PULSAR_HOST}
ENV PULSAR_PORT=${PULSAR_PORT}
ENV ELASTIC_INDEX=${ELASTIC_INDEX}
ENV ELASTIC_PORT=${ELASTIC_PORT}
ENV ELASTIC_HOST=${ELASTIC_HOST}
ENV CONSUMER_TOPIC=${CONSUMER_TOPIC}

# copy lib
COPY ../lib /lib

# copy app
COPY ../app/elasticsearch_connector.py /elasticsearch_connector.py

# run
ENTRYPOINT ["python", "/elasticsearch_connector.py"]
