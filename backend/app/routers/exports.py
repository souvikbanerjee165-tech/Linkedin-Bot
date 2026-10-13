from fastapi import APIRouter, HTTPException, Response, Body
from typing import List, Dict, Any, Optional
from app import crud
from app.services.export_engine import export_engine

router = APIRouter(prefix="/api/exports", tags=["Exports"])

@router.get("/clipboard/{draft_id}")
def get_clipboard_text(draft_id: int):
    draft = crud.get_post_draft_by_id(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    fmt = draft.get("active_draft_format", "problem_solution")
    content = draft.get("final_edited_content") or draft.get(f"{fmt}_draft") or draft.get("problem_solution_draft") or ""
    clipboard_text = export_engine.format_for_linkedin_clipboard(content)
    
    return {
        "draft_id": draft_id,
        "format": fmt,
        "clipboard_text": clipboard_text,
        "character_count": len(clipboard_text),
        "word_count": len(clipboard_text.split())
    }

@router.get("/markdown/{draft_id}")
def get_markdown_file(draft_id: int):
    draft = crud.get_post_draft_by_id(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    md_content = export_engine.generate_posts_markdown([draft], pack_title=f"Post #{draft_id} - LinkedIn Copy")
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=linkedin_post_{draft_id}.md"}
    )

@router.post("/markdown-pack")
def get_markdown_pack(draft_ids: List[int] = Body(...)):
    drafts = []
    for d_id in draft_ids:
        d = crud.get_post_draft_by_id(d_id)
        if d:
            drafts.append(d)
    
    if not drafts:
        raise HTTPException(status_code=400, detail="No valid drafts found for IDs provided")
    
    md_content = export_engine.generate_posts_markdown(drafts, pack_title="Weekly LinkedIn Content Pack")
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=weekly_linkedin_content_pack.md"}
    )

@router.get("/pdf/{draft_id}")
def get_single_pdf(draft_id: int):
    draft = crud.get_post_draft_by_id(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    pdf_bytes = export_engine.generate_pdf_pack([draft], title=f"LinkedIn Post #{draft_id} Strategy & Copy")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=linkedin_post_{draft_id}.pdf"}
    )

@router.post("/pdf-pack")
def get_pdf_pack(draft_ids: List[int] = Body(...)):
    drafts = []
    for d_id in draft_ids:
        d = crud.get_post_draft_by_id(d_id)
        if d:
            drafts.append(d)
            
    if not drafts:
        # Fallback to all drafts if empty
        drafts = crud.get_post_drafts()[:5]

    if not drafts:
        raise HTTPException(status_code=400, detail="No drafts available to generate PDF pack")

    pdf_bytes = export_engine.generate_pdf_pack(drafts, title="Weekly LinkedIn Content Pack (Executive Copy & Verification)")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=weekly_linkedin_content_pack.pdf"}
    )

@router.get("/calendar-csv")
def get_calendar_csv():
    items = crud.get_calendar_items()
    csv_text = export_engine.generate_calendar_csv(items)
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=linkedin_content_calendar.csv"}
    )
