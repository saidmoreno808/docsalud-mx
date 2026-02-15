# ============================================================
# DocSalud MX — Makefile
# ============================================================

.PHONY: help setup dev test test-unit test-integration lint format \
        docker-build docker-up docker-down migrate seed \
        train-ner train-classifier generate-data clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Setup ───────────────────────────────────────────────────
setup: ## Install dependencies, create .env, download models
	cp -n .env.example .env || true
	cd backend && pip install -r requirements-dev.txt
	cd backend && python -m spacy download es_core_news_lg
	cd frontend && npm install

# ── Development ─────────────────────────────────────────────
dev: ## Start docker-compose dev with hot-reload
	docker compose up --build

dev-backend: ## Start only backend in dev mode
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend: ## Start only frontend in dev mode
	cd frontend && npm run dev

# ── Testing ─────────────────────────────────────────────────
test: ## Run all tests
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing

test-unit: ## Run unit tests only
	cd backend && python -m pytest tests/unit/ -v

test-integration: ## Run integration tests only
	cd backend && python -m pytest tests/integration/ -v

test-e2e: ## Run e2e tests only
	cd backend && python -m pytest tests/e2e/ -v

test-frontend: ## Run frontend tests
	cd frontend && npm run test

# ── Code Quality ────────────────────────────────────────────
lint: ## Run all linters
	cd backend && python -m ruff check app/ tests/
	cd backend && python -m mypy app/
	cd frontend && npm run lint 2>/dev/null || true

format: ## Format code (Black + isort)
	cd backend && python -m black app/ tests/
	cd backend && python -m isort app/ tests/

# ── Docker ──────────────────────────────────────────────────
docker-build: ## Build Docker images
	docker compose build

docker-up: ## Start production containers
	docker compose up -d

docker-down: ## Stop all containers
	docker compose down

docker-logs: ## Tail container logs
	docker compose logs -f

# ── Database ────────────────────────────────────────────────
migrate: ## Run Alembic migrations
	cd backend && python -m alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MSG="description")
	cd backend && python -m alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed initial data
	cd backend && python scripts/seed_database.py

# ── ML Training ─────────────────────────────────────────────
generate-data: ## Generate synthetic training data
	cd backend && python scripts/generate_synthetic_data.py

train-ner: ## Train SpaCy NER model
	cd backend && python scripts/train_ner_model.py

train-classifier: ## Train document classifier
	cd backend && python scripts/train_classifier.py

train-transformer: ## Fine-tune transformer model
	cd backend && python scripts/train_transformer.py

evaluate: ## Evaluate all models
	cd backend && python scripts/evaluate_models.py

# ── Cleanup ─────────────────────────────────────────────────
clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage
	rm -rf frontend/node_modules frontend/dist
