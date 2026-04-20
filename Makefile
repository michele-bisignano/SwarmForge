griffe-dump:
	uv run python -m griffe dump src \
		--output docs/api/swarmforge.json \
		--resolve-aliases

install:
	uv sync

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@echo "Pulizia completata."

.PHONY: griffe-dump install clean
