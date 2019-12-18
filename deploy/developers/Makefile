up:
	docker-compose pull
	docker-compose down
	docker-compose up -d

build:
	@docker-compose build --build-arg PRIVATE_SSH_KEY="$(shell base64 ~/.ssh/id_rsa)"

logs:
	docker-compose logs -f service-exo-core

test:
	docker-compose build client
	docker-compose build test
	docker-compose run --no-deps -d client
	docker-compose run --no-deps test
