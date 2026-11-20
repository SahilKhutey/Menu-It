.PHONY: install lint format test backend-test frontend-test typecheck architecture-test run-backend run-frontend seed validate-e2e clean

install:
	cd backend && pip install -r requirements.txt
	cd frontend && pnpm install

lint:
	cd backend && ruff check .
	cd frontend && pnpm run lint

format:
	cd backend && ruff format .
	cd frontend && npx prettier --write "src/**/*.{ts,tsx,css,json}"

test: backend-test frontend-test

backend-test:
	pytest tests/ -v

frontend-test:
	cd frontend && pnpm run build

typecheck:
	cd frontend && npx tsc --noEmit

architecture-test:
	pytest tests/architecture -v

run-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

run-frontend:
	cd frontend && pnpm run dev

seed:
	cd backend && python -m app.seed

validate-e2e:
	python scripts/validate_arc02_e2e.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
