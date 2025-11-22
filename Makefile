.PHONY: help install test lint format clean build docker run-tests coverage docs

# Default target
help:
	@echo "IPv6-Only Tools - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install package and dependencies"
	@echo "  make install-dev    Install with development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run all tests"
	@echo "  make test-python    Run Python tests"
	@echo "  make test-go        Run Go tests"
	@echo "  make coverage       Run tests with coverage"
	@echo "  make benchmark      Run performance benchmarks"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run linters"
	@echo "  make format         Format code"
	@echo "  make security       Run security checks"
	@echo ""
	@echo "Build:"
	@echo "  make build          Build all components"
	@echo "  make build-go       Build Go tools"
	@echo "  make build-python   Build Python package"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   Build Docker image"
	@echo "  make docker-run     Run Docker container"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs           Generate documentation"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          Remove build artifacts"
	@echo ""

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Testing
test: test-python test-go

test-python:
	pytest tests/python/ -v

test-go:
	cd src/go && go test -v ./...

run-tests: test

coverage:
	pytest tests/python/ --cov=ipv6tools --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

benchmark:
	python -m ipv6tools.benchmark -n 10000

# Code quality
lint: lint-python lint-go lint-shell

lint-python:
	flake8 src/python/ipv6tools/
	@echo "Python linting complete"

lint-go:
	cd src/go && go vet ./...
	cd src/go && gofmt -l .
	@echo "Go linting complete"

lint-shell:
	shellcheck src/scripts/*.sh || true
	@echo "Shell linting complete"

format: format-python format-go

format-python:
	black src/python/ipv6tools/
	@echo "Python formatting complete"

format-go:
	cd src/go && gofmt -w .
	@echo "Go formatting complete"

security:
	bandit -r src/python/ipv6tools/ || true
	safety check || true

# Building
build: build-python build-go

build-python:
	python -m build
	@echo "Python package built in dist/"

build-go:
	mkdir -p bin
	cd src/go && go build -o ../../bin/ipv6-ping ./cmd/ipv6-ping
	cd src/go && go build -o ../../bin/ipv6-scan ./cmd/ipv6-scan
	@echo "Go binaries built in bin/"

# Docker
docker-build:
	docker build -t ipv6-only:latest .

docker-run:
	docker run -it --rm ipv6-only:latest

# Documentation
docs:
	@echo "Documentation is in docs/ directory"
	@echo "Open docs/TUTORIAL.md for getting started"

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf bin/
	@echo "Cleanup complete"

# Development helpers
dev-setup: install-dev
	@echo "Development environment ready!"
	@echo "Run 'make test' to verify installation"

quick-test:
	pytest tests/python/ -v -x --tb=short

watch-tests:
	pytest-watch tests/python/ -v
