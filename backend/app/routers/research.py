from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
from app import crud
from app.schemas import ResearchItemResponse, ResearchItemCreate
from app.services.signal_inspector import signal_inspector

router = APIRouter(prefix="/api/research", tags=["Research"])

@router.get("", response_model=List[ResearchItemResponse])
def get_research():
    return crud.get_research_items()

@router.post("", response_model=ResearchItemResponse)
def add_research_item(payload: ResearchItemCreate):
    created = crud.create_research_item(payload.model_dump())
    return created

@router.post("/inspect-url")
async def inspect_website_url(payload: Dict[str, str] = Body(...)):
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        signals = await signal_inspector.inspect_website(url)
        
        # Save as structured research note automatically
        title = f"Signal Audit: {signals.get('page_title') or url}"
        synthesized = "; ".join(signals.get("observable_bottlenecks", []))
        
        crud.create_research_item({
            "title": title,
            "source_url": url,
            "source_type": "website_audit",
            "raw_excerpt": f"Opportunity Score: {signals.get('opportunity_score')}/100. Load time: {signals.get('load_time_seconds')}s.",
            "analyst_notes": signals.get("outreach_angle", ""),
            "synthesized_problems": synthesized,
            "buyer_questions": "Why do prospective patients drop off before booking?",
            "industry_vocabulary": "online booking widget, patient triage, mobile load time",
            "tags": "playwright_audit, dental_sales_intel"
        })

        return signals
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to inspect website: {str(exc)}")
