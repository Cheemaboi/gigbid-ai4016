from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_approval_is_idempotent_preview():
    run = client.post("/jobs/job-1001/run").json()
    draft_id = run["draft"]["id"]
    response = client.post(f"/proposals/{draft_id}/approve", json={"idempotency_key": "reviewer-demo-001"})
    assert response.status_code == 200
    assert response.json()["dry_run_preview"]["dry_run"] is True


def test_attributed_real_job_sample_is_available_for_research():
    response = client.get("/research/upwork-2024?limit=2")
    assert response.status_code == 200
    payload = response.json()
    assert payload["metadata"]["source_type"] == "real_public_dataset"
    assert len(payload["records"]) == 2
    assert payload["records"][0]["provenance"]["license"] == "ODC Attribution License (ODC-By)"

