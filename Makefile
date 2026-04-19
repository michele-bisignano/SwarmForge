# Core Makefile for SwarmForge
# Developed according to universal coding standards.

# Directories
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := Docs
SCRIPTS_DIR := scripts

# Dependencies
.PHONY: all clean setup build test contract docs

# Default target: Runs setup and initial build/test checks.
all: setup build test

# ----------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------
setup: venv
	@echo "--- Setting up project environment ---"
	# Install core dependencies (e.g., Poetry/Pipenv environment)
	python -m venv venv
	source venv/bin/activate
	# Install required development and runtime dependencies
	uv pip install -r requirements.txt

venv:
	@echo "--- Creating virtual environment ---"
	python -m venv venv

# ----------------------------------------------------------------------
# Build/Contract/Docs
# ----------------------------------------------------------------------

# Dependency: Requires core libs and griffe installed.
contract: setup
	@echo "--- Generating griffe API documentation (Mandatory step) ---"
	python scripts/extract_contract_doc.py \
		--api-json Docs/api/SwarmForge.json \
		--class ExampleService \
		--methods run_task \
		--output Docs/snippets/ExampleService_snippet.md

# Placeholder command: Assume griffe dump was done manually or via setup
# make griffe-dump
# python scripts/extract_contract_doc.py ...

docs:
	@echo "--- Generating all documentation snippets ---"
	# Placeholder for calling multiple contract documents
	@echo "Run 'contract' for specific service documentation."

# ----------------------------------------------------------------------
# Test
# ----------------------------------------------------------------------
test: setup
	@echo "--- Running full test suite ---"
	# Run all parametrized tests
	pytest ${TEST_DIR} -v --tb=short --asyncio-mode=auto

# ----------------------------------------------------------------------
# Development & Utility
# ----------------------------------------------------------------------
build: test
	@echo "--- Building final application artifacts ---"
	# Replace with actual build commands (e.g., Poetry build or FastAPI startup)

clean:
	@echo "--- Cleaning project artifacts ---"
	rm -rf venv build dist *.pyc