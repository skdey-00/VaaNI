# VaaNI Makefile
# Convenience commands for development, testing, and deployment

.PHONY: help install dev test demo docker-build docker-up docker-down lint format clean

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[0;33m
NC := \033[0m # No Color

## help: Show this help message
help:
	@echo '$(BLUE)VaaNI Banking Assistant - Available Commands$(NC)'
	@echo ''
	@echo 'Usage: make [target]'
	@echo ''
	@echo '$(GREEN)Development:$(NC)'
	@echo '  make install      - Install all dependencies'
	@echo '  make dev          - Start all services in development mode'
	@echo '  make lint         - Run linting on all services'
	@echo '  make format       - Format code with black and prettier'
	@echo ''
	@echo '$(GREEN)Testing:$(NC)'
	@echo '  make test         - Run all integration tests'
	@echo '  make test-unit    - Run unit tests only'
	@echo '  make test-integration - Run integration tests only'
	@echo '  make coverage     - Run tests with coverage report'
	@echo ''
	@echo '$(GREEN)Demo:$(NC)'
	@echo '  make demo         - Run FD demo scenario'
	@echo '  make demo-audio   - Generate demo audio files'
	@echo ''
	@echo '$(GREEN)Docker:$(NC)'
	@echo '  make docker-build - Build all Docker images'
	@echo '  make docker-up    - Start services with docker-compose'
	@echo '  make docker-down  - Stop docker-compose services'
	@echo '  make docker-logs  - Show docker-compose logs'
	@echo '  make docker-clean - Remove all docker containers and volumes'
	@echo ''
	@echo '$(GREEN)Utilities:$(NC)'
	@echo '  make clean        - Remove generated files and caches'
	@echo '  make deps         - Update dependencies'
	@echo '  make check        - Check if required tools are installed'

## install: Install all Python and Node dependencies
install:
	@echo '$(BLUE)Installing dependencies...$(NC)'
	@cd gateway && pip install -r requirements.txt
	@cd voice_service && pip install -r requirements.txt
	@cd llm_service && pip install -r requirements.txt
	@cd frontend && npm install
	@echo '$(GREEN)✅ All dependencies installed$(NC)'

## dev: Start all services in development mode
dev:
	@echo '$(BLUE)Starting development servers...$(NC)'
	@echo 'Gateway: http://localhost:8000'
	@echo 'Voice Service: http://localhost:8001'
	@echo 'LLM Service: http://localhost:8002'
	@echo 'Frontend: http://localhost:5173'
	@echo ''
	@echo '$(YELLOW)Press Ctrl+C to stop all services$(NC)'
	@make -j4 dev-gateway dev-voice dev-llm dev-frontend

dev-gateway:
	@cd gateway && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-voice:
	@cd voice_service && uvicorn main:app --reload --host 0.0.0.0 --port 8001

dev-llm:
	@cd llm_service && uvicorn main:app --reload --host 0.0.0.0 --port 8002

dev-frontend:
	@cd frontend && npm run dev

## lint: Run linting on all services
lint:
	@echo '$(BLUE)Linting Python code...$(NC)'
	@cd gateway && ruff check . || true
	@cd voice_service && ruff check . || true
	@cd llm_service && ruff check . || true
	@echo '$(BLUE)Linting TypeScript code...$(NC)'
	@cd frontend && npm run lint || true
	@echo '$(GREEN)✅ Linting complete$(NC)'

## format: Format code with black and prettier
format:
	@echo '$(BLUE)Formatting Python code...$(NC)'
	@cd gateway && black . || true
	@cd voice_service && black . || true
	@cd llm_service && black . || true
	@echo '$(BLUE)Formatting TypeScript code...$(NC)'
	@cd frontend && npm run format || true
	@echo '$(GREEN)✅ Formatting complete$(NC)'

## test: Run all integration tests
test:
	@echo '$(BLUE)Running integration tests...$(NC)'
	@echo '$(YELLOW)Note: Make sure services are running with "make docker-up"$(NC)'
	@pytest tests/ -v --tb=short
	@echo '$(GREEN)✅ Tests complete$(NC)'

## test-unit: Run unit tests only
test-unit:
	@echo '$(BLUE)Running unit tests...$(NC)'
	@pytest tests/ -m "unit" -v

## test-integration: Run integration tests only
test-integration:
	@echo '$(BLUE)Running integration tests...$(NC)'
	@pytest tests/ -m "integration" -v

## coverage: Run tests with coverage report
coverage:
	@echo '$(BLUE)Running tests with coverage...$(NC)'
	@pytest tests/ --cov=gateway --cov=voice_service --cov=llm_service --cov-report=html --cov-report=term
	@echo '$(GREEN)✅ Coverage report: htmlcov/index.html$(NC)'

## demo: Run FD demo scenario
demo:
	@echo '$(BLUE)Running FD demo scenario...$(NC)'
	@echo '$(YELLOW)Note: Make sure services are running$(NC)'
	@python demo/scenario_fd.py

## demo-audio: Generate demo audio files
demo-audio:
	@echo '$(BLUE)Generating demo audio files...$(NC)'
	@python demo/seed_audio.py
	@echo '$(GREEN)✅ Demo audio generated in demo/audio/$(NC)'

## docker-build: Build all Docker images
docker-build:
	@echo '$(BLUE)Building Docker images...$(NC)'
	docker-compose build
	@echo '$(GREEN)✅ Docker images built$(NC)'

## docker-up: Start services with docker-compose
docker-up:
	@echo '$(BLUE)Starting services with docker-compose...$(NC)'
	docker-compose up -d
	@echo '$(GREEN)✅ Services started$(NC)'
	@echo 'Gateway: http://localhost:8000'
	@echo 'Voice Service: http://localhost:8001'
	@echo 'LLM Service: http://localhost:8002'
	@echo 'Frontend: http://localhost:5173'
	@echo ''
	@echo 'Run "make docker-logs" to view logs'

## docker-down: Stop docker-compose services
docker-down:
	@echo '$(BLUE)Stopping docker-compose services...$(NC)'
	docker-compose down
	@echo '$(GREEN)✅ Services stopped$(NC)'

## docker-logs: Show docker-compose logs
docker-logs:
	docker-compose logs -f

## docker-clean: Remove all docker containers and volumes
docker-clean:
	@echo '$(RED)Removing all docker containers and volumes...$(NC)'
	docker-compose down -v
	docker system prune -f
	@echo '$(GREEN)✅ Docker cleanup complete$(NC)'

## clean: Remove generated files and caches
clean:
	@echo '$(BLUE)Cleaning generated files...$(NC)'
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@rm -rf .pytest_cache .coverage htmlcov
	@rm -rf frontend/dist frontend/node_modules/.vite
	@cd frontend && rm -rf dist
	@echo '$(GREEN)✅ Clean complete$(NC)'

## deps: Update dependencies
deps:
	@echo '$(BLUE)Updating dependencies...$(NC)'
	@cd gateway && pip install -U -r requirements.txt
	@cd voice_service && pip install -U -r requirements.txt
	@cd llm_service && pip install -U -r requirements.txt
	@cd frontend && npm update
	@echo '$(GREEN)✅ Dependencies updated$(NC)'

## check: Check if required tools are installed
check:
	@echo '$(BLUE)Checking required tools...$(NC)'
	@command -v python3 >/dev/null 2>&1 || echo "$(RED)❌ Python 3 not found$(NC)"
	@command -v node >/dev/null 2>&1 || echo "$(RED)❌ Node.js not found$(NC)"
	@command -v docker >/dev/null 2>&1 || echo "$(RED)❌ Docker not found$(NC)"
	@command -v pytest >/dev/null 2>&1 || echo "$(RED)❌ pytest not found$(NC)"
	@echo '$(GREEN)✅ All tools installed$(NC)'
