FROM --platform=linux/amd64 python:3.9.10

# update pip
RUN /usr/local/bin/python -m pip install --upgrade pip

# install model dependencies
COPY ../requirements/model_requirements.txt /requirements.txt
RUN pip install -r /requirements.txt \
    && rm /requirements.txt


# set environment variables
ARG PULSAR_HOST
ARG PULSAR_PORT
ARG MODEL_NAME
ENV MODEL_NAME=${MODEL_NAME}
ENV PULSAR_HOST=${PULSAR_HOST}
ENV PULSAR_PORT=${PULSAR_PORT}

# copy lib
COPY ../lib /lib

# copy decoy app
COPY ../app/decoy.py /decoy.py

# run
ENTRYPOINT ["python", "/decoy.py"]