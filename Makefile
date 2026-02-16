# ============================================================
# DocSalud MX — Makefile
# ============================================================

.PHONY: help setup dev test test-unit test-integration test-e2e test-frontend \
        lint format docker-build docker-up docker-down docker-logs \
        docker-prod-build docker-prod-up docker-prod-down docker-prod-logs \
        migrate migrate-create seed \
        train-ner train-classifier train-transformer generate-data evaluate \
        clean pre-commit-install ssl-init backup

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

# ── Setup ───────────────────────────────────────────────────
setup: ## Install dependencies, create .env, download models
	cp -n .env.example .env || true
	cd backend && pip install -r requirements-dev.txt
	cd backend && python -m spacy download es_core_news_lg
	cd frontend && npm install
	$(MAKE) pre-commit-install

pre-commit-install: ## Install pre-commit hooks
	pip install pre-commit
	pre-commit install

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

test-all: ## Run backend + frontend tests
	$(MAKE) test
	$(MAKE) test-frontend

# ── Code Quality ────────────────────────────────────────────
lint: ## Run all linters
	cd backend && python -m ruff check app/ tests/
	cd backend && python -m mypy app/ --ignore-missing-imports
	cd frontend && npm run lint 2>/dev/null || true

format: ## Format code (Black + isort)
	cd backend && python -m black app/ tests/ --line-length 100
	cd backend && python -m isort app/ tests/ --profile black --line-length 100

# ── Docker (Development) ────────────────────────────────────
docker-build: ## Build dev Docker images
	docker compose build

docker-up: ## Start dev containers
	docker compose up -d

docker-down: ## Stop dev containers
	docker compose down

docker-logs: ## Tail dev container logs
	docker compose logs -f

# ── Docker (Production) ─────────────────────────────────────
docker-prod-build: ## Build production Docker images
	docker compose -f docker-compose.prod.yml build

docker-prod-up: ## Start production containers
	docker compose -f docker-compose.prod.yml up -d

docker-prod-down: ## Stop production containers
	docker compose -f docker-compose.prod.yml down

docker-prod-logs: ## Tail production container logs
	docker compose -f docker-compose.prod.yml logs -f

docker-prod-restart: ## Restart production backend
	docker compose -f docker-compose.prod.yml restart backend nginx

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

# ── SSL / Certbot ───────────────────────────────────────────
ssl-init: ## Initialize SSL certificate with Let's Encrypt (usage: make ssl-init DOMAIN=yourdomain.com)
	docker compose -f docker-compose.prod.yml run --rm certbot \
		certbot certonly --webroot -w /var/www/certbot \
		-d $(DOMAIN) --agree-tos --no-eff-email --email admin@$(DOMAIN)
	docker compose -f docker-compose.prod.yml restart nginx

ssl-renew: ## Renew SSL certificates
	docker compose -f docker-compose.prod.yml run --rm certbot certbot renew --quiet
	docker compose -f docker-compose.prod.yml restart nginx

# ── Backup ──────────────────────────────────────────────────
backup: ## Backup PostgreSQL database
	bash infrastructure/scripts/backup.sh

# ── Cleanup ─────────────────────────────────────────────────
clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage
	rm -rf frontend/dist

clean-docker: ## Remove all Docker artifacts (containers, images, volumes)
	docker compose down -v --rmi all 2>/dev/null || true
	docker compose -f docker-compose.prod.yml down -v --rmi all 2>/dev/null || true
