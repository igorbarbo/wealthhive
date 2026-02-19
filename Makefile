.PHONY: install dev-install test lint format clean docker-build docker-up docker-down migrate seed

# Instalação
install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements-dev.txt

# Poetry
poetry-install:
	poetry install

poetry-update:
	poetry update

# Desenvolvimento
run-api:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	streamlit run frontend/app.py

run-worker:
	celery -A infrastructure.message_queue.celery_tasks worker --loglevel=info

run-flower:
	celery -A infrastructure.message_queue.celery_tasks flower

# Banco de Dados
migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(message)"

seed:
	python scripts/seed_data.py

# Testes
test:
	pytest tests/ -v --cov=.

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-e2e:
	pytest tests/e2e/ -v

# Qualidade de Código
lint:
	flake8 app/ core/ infrastructure/ ml/ nlp/ backtest/ quant/ websocket/ fundamental/ frontend/ monitoring/
	mypy app/ core/ infrastructure/

format:
	black .
	isort .

format-check:
	black --check .
	isort --check-only .

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-prod-up:
	docker-compose -f docker-compose.prod.yml up -d

# Limpeza
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/ dist/ .eggs/

# Documentação
docs-serve:
	mkdocs serve

docs-build:
	mkdocs build

# Utilitários
backup:
	python scripts/backup.py

deploy-staging:
	./scripts/deploy.sh staging

deploy-production:
	./scripts/deploy.sh production
