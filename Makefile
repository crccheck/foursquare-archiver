help: ## Shows this help
	@echo "$$(grep -h '#\{2\}' $(MAKEFILE_LIST) | sed 's/: #\{2\} /	/' | column -t -s '	')"

install: ## Install requirements
	uv sync

lint: ## Lint the code
	uv run ruff check .
	uv run ruff format .

docker/build: ## Build the Docker image
	docker build -t crccheck/foursquare-archiver .
