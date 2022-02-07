FROM --platform=linux/amd64 python:3.9.10

# update pip
RUN /usr/local/bin/python -m pip install --upgrade pip

# install model dependencies
COPY ../requirements/model_requirements.txt /requirements.txt
RUN pip install -r /requirements.txt \
    && rm /requirements.txt

# copy model
ARG SRC_MODEL_PATH
ARG TGT_MODEL_PATH
COPY ${SRC_MODEL_PATH} ${TGT_MODEL_PATH}

# set environment variables
ARG PULSAR_HOST
ARG PULSAR_PORT
ARG MODEL_NAME
ARG MODEL_VERSION
ARG CONSUMER_TOPIC
ENV MODEL_PATH=${TGT_MODEL_PATH}
ENV MODEL_NAME=${MODEL_NAME}
ENV PULSAR_HOST=${PULSAR_HOST}
ENV PULSAR_PORT=${PULSAR_PORT}
ENV MODEL_VERSION=${MODEL_VERSION}
ENV CONSUMER_TOPIC=${CONSUMER_TOPIC}

# copy lib
COPY ../lib /lib

# copy predict app
COPY ../app/predict.py /predict.py

# run
ENTRYPOINT ["python", "/predict.py"]
