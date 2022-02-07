.PHONY: all
all: up

.PHONY: up
up: 
	docker compose --env-file docker_vars.env up --build --force-recreate lr_model dt_model pulsar score decoy_model log_collector score_collector elastic_search kibana log_elasticsearch_connector score_elasticsearch_connector

.PHONY: down
down: 
	docker compose --env-file docker_vars.env down -v --remove-orphans

.PHONY: train-canary
train-canary:
	python scripts/train_models.py LogisticRegression

.PHONY: train-model
train-model:
	python scripts/train_models.py DecisionTree
