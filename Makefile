SHELL := /bin/zsh

.PHONY: bootstrap dev dev-web dev-api migrate-api lint format test

bootstrap:
	./scripts/bootstrap.sh

dev:
	./scripts/dev.sh

dev-web:
	./scripts/dev-web.sh

dev-api:
	./scripts/dev-api.sh

migrate-api:
	./scripts/migrate-api.sh

lint:
	./scripts/lint.sh

format:
	./scripts/format.sh

test:
	./scripts/test.sh
