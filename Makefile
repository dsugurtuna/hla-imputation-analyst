.PHONY: help install dev-install lint format test test-cov clean build docker-build docker-run docs

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
DOCKER_IMAGE := hla-imputation-analyst
VERSION := $(shell cat VERSION 2>/dev/null || echo "1.0.0")

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ Help
help: ## Display this help message
	@echo "$(BLUE)HLA Imputation Analyst - Development Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Installation
install: ## Install package in production mode
	@echo "$(BLUE)Installing HLA Imputation Analyst...$(NC)"
	$(PIP) install -e .

dev-install: ## Install package with development dependencies
	@echo "$(BLUE)Installing HLA Imputation Analyst (development mode)...$(NC)"
	$(PIP) install -e ".[all]"
	pre-commit install
	@echo "$(GREEN)✓ Development environment ready$(NC)"

##@ Code Quality
lint: ## Run linting checks (ruff, mypy)
	@echo "$(BLUE)Running linters...$(NC)"
	$(PYTHON) -m ruff check src/ tests/
	$(PYTHON) -m mypy src/

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	$(PYTHON) -m black src/ tests/
	$(PYTHON) -m isort src/ tests/
	$(PYTHON) -m ruff check --fix src/ tests/
	@echo "$(GREEN)✓ Code formatted$(NC)"

check: lint ## Run all checks (lint + type check)
	@echo "$(GREEN)✓ All checks passed$(NC)"

##@ Testing
test: ## Run test suite
	@echo "$(BLUE)Running tests...$(NC)"
	$(PYTEST) tests/ -v

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(PYTEST) tests/ --cov=src/hla_analyst --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

test-unit: ## Run unit tests only
	$(PYTEST) tests/ -v -m unit

test-integration: ## Run integration tests only
	$(PYTEST) tests/ -v -m integration

##@ Build & Distribution
build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)✓ Packages built in dist/$(NC)"

clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf htmlcov/ .coverage coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Clean complete$(NC)"

##@ Docker
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t $(DOCKER_IMAGE):$(VERSION) -t $(DOCKER_IMAGE):latest .
	@echo "$(GREEN)✓ Docker image built: $(DOCKER_IMAGE):$(VERSION)$(NC)"

docker-run: ## Run analysis in Docker container
	@echo "$(BLUE)Running HLA Analyst in Docker...$(NC)"
	docker run --rm -v $(PWD)/data:/data $(DOCKER_IMAGE):latest analyze /data/sample_batch

docker-test: ## Run tests in Docker container
	docker run --rm $(DOCKER_IMAGE):latest pytest tests/ -v

##@ Documentation
docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	mkdocs build
	@echo "$(GREEN)✓ Documentation built in site/$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation at http://localhost:8000$(NC)"
	mkdocs serve

##@ Analysis Commands
analyze: ## Run analysis on sample data (usage: make analyze BATCH=./data/sample)
	@echo "$(BLUE)Running HLA imputation analysis...$(NC)"
	$(PYTHON) -m hla_analyst analyze $(BATCH)

report: ## Generate HTML report (usage: make report BATCH=./data/sample)
	@echo "$(BLUE)Generating analysis report...$(NC)"
	$(PYTHON) -m hla_analyst analyze $(BATCH) --format html --output report.html

validate: ## Validate batch integrity (usage: make validate BATCH=./data/sample)
	@echo "$(BLUE)Validating batch integrity...$(NC)"
	$(PYTHON) -m hla_analyst validate $(BATCH)

##@ CI/CD
ci: lint test ## Run CI pipeline locally
	@echo "$(GREEN)✓ CI pipeline passed$(NC)"

release: ## Create a new release (usage: make release VERSION=1.0.1)
	@echo "$(BLUE)Creating release $(VERSION)...$(NC)"
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	git push origin v$(VERSION)
	@echo "$(GREEN)✓ Release v$(VERSION) created$(NC)"
