.PHONY: db up down backend frontend backfill

db:
	docker compose up -d

down:
	docker compose down

backend:
	cd backend && . .venv/bin/activate 2>/dev/null || true; uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

backfill:
	cd backend && python -m app.ingest.run_backfill

phase2:
	cd backend && python -m app.ingest.run_phase2
