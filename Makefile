all: help

help: ## Print this help message
	@grep -E '^[a-zA-Z._-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: hello
hello: ## Print "Hello, World!"
	echo "Hello, World!"

.PHONY: run
run: ## Run the application
	uv run app/main.py

.PHONY: build
build: ## Build the container image and sync artifact registry
	docker build --platform linux/amd64 -t gcr.io/<your-project-name>/adk-oauth-sample:latest .
	docker push gcr.io/<your-project-name>/adk-oauth-sample:latest

.PHONY: replace
replace: ## Replace the Cloud Run service with the configuration in cloudrun.yaml
	gcloud run services replace cloudrun.yaml \
		--region <location> \
		--platform managed \
		--project <your-project-name>

.PHONY: stop
stop: ## Stop the Cloud Run service
	gcloud run services delete adk-oauth-sample \
		--region <location> \
		--platform managed \
		--project <your-project-name> \
		--quiet
