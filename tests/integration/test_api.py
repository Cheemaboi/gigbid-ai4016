from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_approval_is_idempotent_preview():
    run = client.post("/jobs/job-1001/run").json()
    draft_id = run["draft"]["id"]
    response = client.post(f"/proposals/{draft_id}/approve", json={"idempotency_key": "reviewer-demo-001"})
    assert response.status_code == 200
    assert response.json()["dry_run_preview"]["dry_run"] is True

