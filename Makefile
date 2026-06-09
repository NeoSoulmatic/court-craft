BACKEND_UVICORN := backend/.venv/bin/uvicorn

.PHONY: db up down stack backend frontend backfill phase2 phase2b phase3 playoffs daily

db:
	docker compose up -d db

down:
	docker compose --profile full down

stack:
	docker compose --profile full up --build -d

stack-logs:
	docker compose --profile full logs -f

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

phase3:
	cd backend && .venv/bin/python ../ml/run_phase3.py

playoffs:
	cd backend && .venv/bin/python -m app.ingest.run_playoffs
	cd backend && PYTHONPATH=.. .venv/bin/python ../ml/predict.py

daily:
	cd backend && .venv/bin/python -m app.ingest.run_daily
