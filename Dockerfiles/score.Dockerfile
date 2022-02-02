FROM --platform=linux/amd64 python:3.9.10

# update pip
RUN /usr/local/bin/python -m pip install --upgrade pip

# install model dependencies
RUN pip install "fastapi==0.73.0" \
    "uvicorn==0.16.0" \
    "pulsar-client==2.9.1"

# set environment variables
ARG PULSAR_HOST
ARG PULSAR_PORT
ARG TIMEOUT
ARG NUM_MODELS
ARG RET_TOPIC
ENV PULSAR_HOST=${PULSAR_HOST}
ENV PULSAR_PORT=${PULSAR_PORT}
ENV TIMEOUT=${TIMEOUT}
ENV NUM_MODELS=${NUM_MODELS}
ENV RET_TOPIC=${RET_TOPIC}

# copy lib
COPY ../lib /lib

# copy predict app
COPY ../app/score.py /score.py

# run
ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/" ,"score:app"]
