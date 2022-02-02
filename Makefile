.PHONY: all
all: up

.PHONY: up
up: 
	docker compose up --build --force-recreate lr_model dt_model pulsar score decoy_model log_collector score_collector

.PHONY: down
down: 
	docker compose down -v --remove-orphans
