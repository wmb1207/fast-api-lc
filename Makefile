services:
	docker-compose up postgres

shell:
	docker-compose run --service-ports api ash

db-shell:
	docker exec -it $(shell docker ps --filter name='fast_api_test_postgres' --format "{{ .ID }}") ash

test_post:
	curl -X POST -d '{"id": 2, "name": "Wenceslao", "description": "this is just a test"}' -H 'Content-Type: application/json' localhost:8000
