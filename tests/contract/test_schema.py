from apps.api.main import app

def test_openapi_exposes_human_approval_contract():
    schema = app.openapi()
    assert "/proposals/{draft_id}/approve" in schema["paths"]
    assert "ApprovalRequest" in schema["components"]["schemas"]

