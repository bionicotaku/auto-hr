SHELL := /bin/zsh

.PHONY: bootstrap dev dev-web dev-api lint format test

bootstrap:
	./scripts/bootstrap.sh

dev:
	./scripts/dev.sh

dev-web:
	./scripts/dev-web.sh

dev-api:
	./scripts/dev-api.sh

lint:
	./scripts/lint.sh

format:
	./scripts/format.sh

test:
	./scripts/test.sh
