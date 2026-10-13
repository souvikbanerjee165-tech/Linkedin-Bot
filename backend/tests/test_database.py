import pytest
import os
import sqlite3
from app.config import settings
from app.database import init_db, seed_initial_data_if_empty, get_connection, create_database_backup, restore_database_backup
from app import crud

def test_database_initialization_and_seeding(tmp_path, monkeypatch):
    test_db = tmp_path / "test_copilot.db"
    monkeypatch.setattr(settings, "database_path", str(test_db))
    monkeypatch.setattr(settings, "backup_dir", str(tmp_path / "backups"))
    
    init_db()
    seed_initial_data_if_empty()
    
    # Verify tables exist
    conn = get_connection()
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    conn.close()
    
    expected = [
        "profile_brand", "knowledge_items", "products", "writing_samples",
        "voice_profile", "content_calendar", "post_drafts", "research_items",
        "post_performance", "api_usage_logs"
    ]
    for table in expected:
        assert table in tables, f"Expected table {table} to exist"

def test_products_seeded_with_concept_distinction(tmp_path, monkeypatch):
    test_db = tmp_path / "test_copilot.db"
    monkeypatch.setattr(settings, "database_path", str(test_db))
    init_db()
    seed_initial_data_if_empty()
    
    products = crud.get_products()
    assert len(products) == 3
    
    keys = {p["product_key"] for p in products}
    assert "podleads_ai" in keys
    assert "dental_sales_intel" in keys
    assert "dental_os_front_desk" in keys
    
    # Verify Dental OS has concept capabilities clearly segregated
    dental_os = crud.get_product_by_key("dental_os_front_desk")
    assert dental_os is not None
    assert len(dental_os["concept_capabilities"]) > 0
    assert any("VoIP" in c or "concept" in c.lower() for c in dental_os["concept_capabilities"])

def test_knowledge_base_5_tier_categories(tmp_path, monkeypatch):
    test_db = tmp_path / "test_copilot.db"
    monkeypatch.setattr(settings, "database_path", str(test_db))
    init_db()
    seed_initial_data_if_empty()
    
    items = crud.get_knowledge_items()
    assert len(items) >= 4
    categories = {i["category"] for i in items}
    assert "verified_fact" in categories
    assert "unverified_hypothesis" in categories
    assert "needs_approval" in categories
    
    # Test adding an item
    new_item = crud.create_knowledge_item({
        "category": "personal_opinion",
        "title": "Agency outreach strategy",
        "claim_content": "Cold DMs without visible business proof perform poorly.",
        "evidence_source": "Personal observations across 50 campaigns",
        "tags": "opinion, outreach",
        "is_verified": False,
        "approved_by_user": True
    })
    assert new_item["id"] is not None
    assert new_item["category"] == "personal_opinion"

def test_backup_and_restore(tmp_path, monkeypatch):
    test_db = tmp_path / "test_copilot.db"
    monkeypatch.setattr(settings, "database_path", str(test_db))
    monkeypatch.setattr(settings, "backup_dir", str(tmp_path / "backups"))
    init_db()
    seed_initial_data_if_empty()
    
    backup_file = create_database_backup()
    assert os.path.exists(backup_file)
    
    # Modify data
    crud.create_knowledge_item({
        "category": "verified_fact",
        "title": "Temp fact",
        "claim_content": "Temporary test fact",
        "is_verified": True
    })
    
    # Restore backup
    assert restore_database_backup(backup_file)
    restored_items = crud.get_knowledge_items()
    # The temporary item should not be in the restored db
    assert not any(i["title"] == "Temp fact" for i in restored_items)
