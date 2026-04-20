griffe-dump:
	uv run python -m griffe dump src \
		--output docs/api/swarmforge.json \
		--resolve-aliases

.PHONY: griffe-dump
