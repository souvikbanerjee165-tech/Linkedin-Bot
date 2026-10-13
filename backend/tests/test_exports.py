import pytest
from app.services.export_engine import export_engine

def test_linkedin_clipboard_formatter():
    raw_md = """# Hook Title
Here is a paragraph.
- Bullet item one
- Bullet item two
## Subheader
Closing statement.
"""
    formatted = export_engine.format_for_linkedin_clipboard(raw_md)
    assert "#" not in formatted
    assert "• Bullet item one" in formatted
    assert "Hook Title" in formatted

def test_calendar_csv_generation():
    items = [
        {
            "scheduled_date": "2026-10-14",
            "day_number": 1,
            "target_reader": "Agency Founders",
            "pillar_name": "Practical AI automation",
            "hook_idea": "Why manual data sorting is costing you 10h weekly",
            "core_argument": "Systems over hype",
            "evidence_needed": "Benchmark audit",
            "intended_response": "Request audit",
            "recommended_format": "problem_solution",
            "commercial_intent": "Spark conversation",
            "status": "scheduled"
        }
    ]
    csv_out = export_engine.generate_calendar_csv(items)
    assert "scheduled_date,day_number" in csv_out
    assert "2026-10-14" in csv_out
    assert "Agency Founders" in csv_out

def test_pdf_generation_valid_output():
    mock_drafts = [
        {
            "id": 1,
            "idea_prompt": "Testing dental clinic inspection signals",
            "active_draft_format": "problem_solution",
            "target_audience": "Dental Practice Owners",
            "buyer_score_total": 88,
            "final_edited_content": "Before buying an outreach tool, inspect public website booking triggers.\n\nHere are 3 signs...",
            "claims_flagged": ["Verify sample clinic inspection count"],
            "visual_suggestion": "Screenshot of website audit scorecard"
        }
    ]
    pdf_bytes = export_engine.generate_pdf_pack(mock_drafts, title="Test Executive Content Pack")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")
