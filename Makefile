services:
	docker-compose up postgres

shell:
	docker-compose run --service-ports api ash

db-shell:
	docker exec -it $(shell docker ps --filter name='fast_api_test_postgres' --format "{{ .ID }}") ash

test_post:
	curl -X POST -d '{"id": 2, "name": "Wenceslao", "description": "this is just a test"}' -H 'Content-Type: application/json' localhost:8000

create_user:
	curl -X POST -d '{"fullname": "Wenceslao", "email": "wenceslao12071@protonmail.com", "phone_number": "3794737096"}' -H 'Content-Type: application/json' localhost:8000/users

delete_user:
	curl -X DELETE -H 'Content-Type: application/json' localhost:8000/users/96

get_users:
	curl -X GET -H 'Content-Type: application/json' localhost:8000/users

