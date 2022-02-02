FROM --platform=linux/amd64 python:3.9.10

# update pip
RUN /usr/local/bin/python -m pip install --upgrade pip

# install model dependencies
RUN pip install "scikit-learn==1.0.2" \
    "fastapi==0.73.0" \
    "uvicorn==0.16.0" \
    "pulsar-client==2.9.1"

# copy model
COPY ../models/dt.model ${MODEL_PATH}

# set environment variables
ENV MODEL_PATH=${MODEL_PATH}
ENV MODEL_NAME=${MODEL_NAME}
ENV PULSAR_HOST=${PULSAR_HOST}
ENV PULSAR_PORT=${PULSAR_PORT}

# copy predict app
COPY ../app/predict.py /predict.py

# run
ENTRYPOINT ["python", "/predict.py"]
