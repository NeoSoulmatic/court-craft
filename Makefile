BACKEND_UVICORN := backend/.venv/bin/uvicorn

.PHONY: db up down backend frontend backfill phase2 phase2b

db:
	docker compose up -d

down:
	docker compose down

backend:
	cd backend && $(BACKEND_UVICORN) app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

backfill:
	cd backend && .venv/bin/python -m app.ingest.run_backfill

phase2:
	cd backend && .venv/bin/python -m app.ingest.run_phase2

phase2b:
	cd backend && .venv/bin/python -m app.ingest.run_phase2b
