import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.database import init_db, seed_initial_data_if_empty

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_api.db"
    monkeypatch.setattr(settings, "database_path", str(test_db))
    monkeypatch.setattr(settings, "backup_dir", str(tmp_path / "backups"))
    monkeypatch.setattr(settings, "deepseek_api_key", "")
    init_db()
    seed_initial_data_if_empty()

client = TestClient(app)

def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_brand_and_audit():
    res = client.get("/api/brand")
    assert res.status_code == 200
    brand = res.json()
    assert "headline" in brand

    # Test audit
    audit_res = client.get("/api/brand/audit")
    assert audit_res.status_code == 200
    audit = audit_res.json()
    assert audit["overall_score"] > 80
    assert len(audit["positioning_options"]) == 3
    assert len(audit["category_audits"]) >= 3

def test_products_matrix():
    res = client.get("/api/products")
    assert res.status_code == 200
    products = res.json()
    assert len(products) == 3
    
    dental_os = [p for p in products if p["product_key"] == "dental_os_front_desk"][0]
    assert len(dental_os["concept_capabilities"]) > 0

def test_knowledge_crud():
    # Create item
    res = client.post("/api/knowledge", json={
        "category": "unverified_hypothesis",
        "title": "Outreach conversion rate hypothesis",
        "claim_content": "Signal-informed messages convert 3x higher than cold blasts.",
        "evidence_source": "Hypothesis based on preliminary agency trial",
        "tags": "conversion, hypothesis",
        "is_verified": False,
        "approved_by_user": False
    })
    assert res.status_code == 200
    created = res.json()
    item_id = created["id"]

    # Retrieve
    get_res = client.get(f"/api/knowledge/{item_id}")
    assert get_res.status_code == 200
    assert get_res.json()["is_verified"] is False

    # Update
    put_res = client.put(f"/api/knowledge/{item_id}", json={"is_verified": True, "approved_by_user": True})
    assert put_res.status_code == 200
    assert put_res.json()["is_verified"] is True

    # Delete
    del_res = client.delete(f"/api/knowledge/{item_id}")
    assert del_res.status_code == 200

def test_post_generation_and_scoring_workflow():
    gen_res = client.post("/api/posts/generate", json={
        "idea_prompt": "I built a system that inspects dental websites for missing online booking widgets.",
        "product_key": "dental_sales_intel",
        "target_audience": "Healthcare Agency Founders",
        "content_pillar": 1,
        "voice_match_level": 0.85
    })
    assert gen_res.status_code == 200
    gen_data = gen_res.json()
    draft_id = gen_data["draft_id"]
    assert "concise" in gen_data["drafts"]
    assert "story" in gen_data["drafts"]
    assert "problem_solution" in gen_data["drafts"]
    assert "technical_breakdown" in gen_data["drafts"]
    assert "demo" in gen_data["drafts"]
    assert "commercial" in gen_data["drafts"]

    # Score
    score_res = client.post(f"/api/posts/{draft_id}/score")
    assert score_res.status_code == 200
    score_data = score_res.json()
    assert 0 <= score_data["total_score"] <= 100

    # Voice feedback calibration
    fb_res = client.post(f"/api/posts/{draft_id}/feedback?feedback_tag=Sounds%20like%20me")
    assert fb_res.status_code == 200
    assert fb_res.json()["success"] is True

def test_calendar_generation_and_csv():
    res = client.post("/api/calendar/generate", json={"days_count": 7})
    assert res.status_code == 200
    entries = res.json()
    assert len(entries) == 7

    csv_res = client.get("/api/exports/calendar-csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]

def test_exports_endpoints():
    # First generate a post
    gen_res = client.post("/api/posts/generate", json={
        "idea_prompt": "YouTube sales intelligence for video editors",
        "product_key": "podleads_ai",
        "target_audience": "Video Editing Agency Founders",
        "content_pillar": 2
    })
    draft_id = gen_res.json()["draft_id"]

    # Clipboard text
    clip_res = client.get(f"/api/exports/clipboard/{draft_id}")
    assert clip_res.status_code == 200
    assert "clipboard_text" in clip_res.json()

    # Markdown export
    md_res = client.get(f"/api/exports/markdown/{draft_id}")
    assert md_res.status_code == 200
    assert "# " in md_res.text

    # PDF export
    pdf_res = client.get(f"/api/exports/pdf/{draft_id}")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF")

    # Multi-post PDF pack
    pack_res = client.post("/api/exports/pdf-pack", json=[draft_id])
    assert pack_res.status_code == 200
    assert pack_res.headers["content-type"] == "application/pdf"

def test_performance_logging_and_attribution():
    log_res = client.post("/api/performance", json={
        "post_title": "Dental Signals Teardown",
        "published_date": "2026-10-14",
        "period_type": "24h",
        "impressions": 1250,
        "reactions": 45,
        "comments": 12,
        "reposts": 3,
        "inbound_dms": 8,
        "qualified_leads": 3,
        "sales_opportunities": 1,
        "revenue_attributed": 2500.0
    })
    assert log_res.status_code == 200

    sum_res = client.get("/api/performance/summary")
    assert sum_res.status_code == 200
    summary = sum_res.json()
    assert summary["total_inbound_dms"] >= 8
    assert summary["total_qualified_leads"] >= 3
    assert summary["total_revenue_attributed"] >= 2500.0

def test_system_status():
    res = client.get("/api/system/status")
    assert res.status_code == 200
    data = res.json()
    assert "total_calls" in data
    assert "current_model" in data

def test_crm_leads():
    res = client.post("/api/performance/leads", json={
        "prospect_name": "Dr. Sarah Mitchell",
        "company": "Apex Dental Group",
        "role_title": "Clinic Owner",
        "stage": "inbound_dm",
        "deal_value_usd": 4500.0,
        "notes": "Interested in automated missed-call triage"
    })
    assert res.status_code == 200
    lead_id = res.json()["id"]

    # Retrieve
    get_res = client.get("/api/performance/leads")
    assert get_res.status_code == 200
    leads = get_res.json()
    assert any(l["id"] == lead_id for l in leads)

    # Update stage
    put_res = client.put(f"/api/performance/leads/{lead_id}", json={"stage": "call_booked"})
    assert put_res.status_code == 200
    assert put_res.json()["stage"] == "call_booked"
