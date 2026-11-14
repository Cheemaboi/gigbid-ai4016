.PHONY: dev api web test eval demo lint seed

api:
	python -m uvicorn apps.api.main:app --reload --port 8000

web:
	cd apps/web && npm install && npm run dev

dev:
	@echo "Run 'make api' and 'make web' in separate terminals."

test:
	python -m pytest -q

eval:
	python evals/runners/run_demo_eval.py

seed:
	python scripts/seed_demo_data.py

demo: seed eval
	@echo "Open the web app and review the seeded job."

lint:
	python -m compileall apps agent rag mcp_servers

