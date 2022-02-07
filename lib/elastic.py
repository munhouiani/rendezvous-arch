import sys

from elasticsearch import Elasticsearch


def get_elastic_client(elastic_host: str, elastic_port: str):
    try:
        es = Elasticsearch(hosts=f"{elastic_host}:{elastic_port}")
        return es
    except:
        sys.exit(1)
