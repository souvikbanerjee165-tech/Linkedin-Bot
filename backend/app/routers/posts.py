from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import json
from app import crud
from app.schemas import (
    PostGenerateRequest, PostGenerateResponse, DraftFormatOutput,
    PostDraftResponse, PostDraftUpdate, BuyerIntentScoringBreakdown
)
from app.services.deepseek_client import deepseek_client
from app.services.scoring_engine import scoring_engine
from app.services.voice_engine import voice_engine

router = APIRouter(prefix="/api/posts", tags=["Posts"])

CONTENT_PILLARS = {
    1: "Business problems that cost companies time or opportunities",
    2: "Practical AI automation demonstrations",
    3: "Behind-the-scenes software building and lessons learned",
    4: "Before-and-after workflow comparisons",
    5: "Industry-specific insights",
    6: "Technical explanations made accessible to business owners",
    7: "Mistakes, trade-offs, and lessons from implementation",
    8: "Case studies based on verified evidence",
    9: "Contrarian but defensible opinions",
    10: "Soft commercial posts that explain what I build and who it helps"
}

@router.post("/generate", response_model=PostGenerateResponse)
async def generate_post(payload: PostGenerateRequest):
    # Retrieve user background & verified knowledge
    brand = crud.get_profile_brand() or {}
    product = crud.get_product_by_key(payload.product_key or "podleads_ai") or {}
    verified_knowledge = crud.get_knowledge_items(category="verified_fact")
    voice_profile = crud.get_voice_profile()

    pillar_name = CONTENT_PILLARS.get(payload.content_pillar or 1, "Practical AI automation demonstrations")

    # Construct strict anti-slop, anti-hallucination system prompt
    system_prompt = (
        "You are an expert B2B LinkedIn content strategist and principal software builder.\n"
        "Your task is to write high-converting, grounded LinkedIn content for a software builder and automation specialist.\n\n"
        "=== STRICT OPERATIONAL CONSTRAINTS ===\n"
        "1. NEVER invent client names, revenue numbers, fake case studies, or unverified results.\n"
        "2. Do NOT use generic AI marketing hype (e.g. 'AI is transforming the world', 'game-changer', 'revolutionize', 'skyrocket').\n"
        "3. Write with concrete technical and operational clarity: mention observable signals, workflow bottlenecks, and system architecture.\n"
        "4. Avoid dramatic emoji walls, hashtags spam, engagement-bait questions ('Agree?', 'Thoughts?'), and manufactured controversy.\n"
        "5. The author builds AI systems, lead intelligence tools, and custom workflow software. Voice is pragmatic, direct, and builder-focused.\n\n"
        "=== AUTHOR & PRODUCT CONTEXT ===\n"
        f"Selected Product: {product.get('name', 'Custom Systems')} - {product.get('description', '')}\n"
        f"Verified Product Capabilities: {', '.join(product.get('verified_capabilities', []))}\n"
        f"Concept Capabilities (MUST NOT BE CLAIMED AS LIVE): {', '.join(product.get('concept_capabilities', []))}\n"
        f"Target Audience: {payload.target_audience}\n"
        f"Content Pillar: {pillar_name}\n"
        f"Voice Profile: Avg Sentence Length ~{voice_profile.get('typical_sentence_length', 14)} words. Formality: {voice_profile.get('formality_level', 0.4)}. Technical: {voice_profile.get('technical_depth', 0.7)}.\n\n"
        "=== REQUIRED OUTPUT FORMAT ===\n"
        "Return a JSON object containing six distinct drafts: concise, story, problem_solution, technical_breakdown, demo, commercial.\n"
        "Each format must include: format_type, title, hook, main_body, closing_line, call_to_action, target_audience, primary_purpose, claims_to_verify (list), suggested_visual, full_text."
    )

    user_prompt = (
        f"Here is my post idea in plain language:\n\"{payload.idea_prompt}\"\n\n"
        f"Target Audience: {payload.target_audience}\n"
        f"Product to highlight: {product.get('name', 'Custom Systems')}\n"
        f"Commercial Intent: {payload.commercial_intent}\n"
        f"Additional Context / Facts: {payload.additional_context}\n\n"
        "Generate all 6 distinct draft formats in JSON according to instructions."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    completion = await deepseek_client.call_completion(
        messages=messages,
        temperature=0.7,
        endpoint_name="post_generation"
    )

    # Parse response JSON
    content_str = completion["content"]
    try:
        # Strip potential markdown code fences
        if "```json" in content_str:
            content_str = content_str.split("```json")[1].split("```")[0].strip()
        elif "```" in content_str:
            content_str = content_str.split("```")[1].split("```")[0].strip()
        parsed_json = json.loads(content_str)
    except Exception:
        # Fallback to structured fallback if json parse fails
        fallback_data = deepseek_client._mock_completion_fallback(messages, "post_generation")
        parsed_json = json.loads(fallback_data["content"])

    # Validate and structure draft formats
    draft_outputs: Dict[str, DraftFormatOutput] = {}
    flagged_claims: List[str] = []
    
    for fmt_key in ["concise", "story", "problem_solution", "technical_breakdown", "demo", "commercial"]:
        raw_draft = parsed_json.get(fmt_key, {})
        full_text = raw_draft.get("full_text") or (
            raw_draft.get("hook", "") + "\n\n" +
            raw_draft.get("main_body", "") + "\n\n" +
            raw_draft.get("closing_line", "") + "\n\n" +
            (raw_draft.get("call_to_action", "") or "")
        ).strip()
        
        claims_list = raw_draft.get("claims_to_verify", [])
        if not claims_list and fmt_key == "demo":
            claims_list = ["Verify demo clinic inspection data before publishing."]
        flagged_claims.extend(claims_list)

        draft_outputs[fmt_key] = DraftFormatOutput(
            format_type=fmt_key,
            title=raw_draft.get("title", fmt_key.replace("_", " ").title()),
            hook=raw_draft.get("hook", ""),
            main_body=raw_draft.get("main_body", ""),
            closing_line=raw_draft.get("closing_line", ""),
            call_to_action=raw_draft.get("call_to_action"),
            target_audience=raw_draft.get("target_audience", payload.target_audience or "B2B Decision Makers"),
            primary_purpose=raw_draft.get("primary_purpose", "B2B Positioning"),
            claims_to_verify=claims_list,
            suggested_visual=raw_draft.get("suggested_visual", "Flowchart or clean terminal screenshot"),
            full_text=full_text
        )

    # Primary draft format defaults to problem_solution
    primary_draft = draft_outputs["problem_solution"]
    scoring_result = scoring_engine.evaluate_draft(
        draft_text=primary_draft.full_text,
        target_audience=payload.target_audience or "",
        product_key=payload.product_key or ""
    )

    # Persist draft to SQLite
    draft_record = {
        "idea_prompt": payload.idea_prompt,
        "product_key": payload.product_key,
        "target_audience": payload.target_audience,
        "content_pillar": pillar_name,
        "voice_match_level": payload.voice_match_level or 0.85,
        "active_draft_format": "problem_solution",
        "concise_draft": draft_outputs["concise"].full_text,
        "story_draft": draft_outputs["story"].full_text,
        "problem_solution_draft": draft_outputs["problem_solution"].full_text,
        "technical_breakdown_draft": draft_outputs["technical_breakdown"].full_text,
        "demo_draft": draft_outputs["demo"].full_text,
        "commercial_draft": draft_outputs["commercial"].full_text,
        "final_edited_content": primary_draft.full_text,
        "buyer_score_total": scoring_result.total_score,
        "buyer_score_breakdown": scoring_result.model_dump(),
        "claims_flagged": list(set(flagged_claims)),
        "visual_suggestion": primary_draft.suggested_visual,
        "feedback_tag": None,
        "status": "draft"
    }

    draft_id = crud.create_post_draft(draft_record)

    return PostGenerateResponse(
        draft_id=draft_id,
        idea_prompt=payload.idea_prompt,
        product_key=payload.product_key,
        drafts=draft_outputs,
        claims_flagged=list(set(flagged_claims)),
        token_usage={
            "prompt_tokens": completion.get("prompt_tokens", 0),
            "completion_tokens": completion.get("completion_tokens", 0),
            "total_tokens": completion.get("total_tokens", 0),
            "model": completion.get("model", "deepseek-chat"),
            "is_mock": completion.get("is_mock", False)
        },
        estimated_cost_usd=completion.get("estimated_cost_usd", 0.0)
    )

@router.get("", response_model=List[PostDraftResponse])
def list_posts(status: Optional[str] = Query(None)):
    return crud.get_post_drafts(status=status)

@router.get("/{draft_id}", response_model=PostDraftResponse)
def get_post_draft(draft_id: int):
    draft = crud.get_post_draft_by_id(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft

@router.put("/{draft_id}", response_model=PostDraftResponse)
def update_post_draft(draft_id: int, payload: PostDraftUpdate):
    updated = crud.update_post_draft(draft_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Draft not found")
    return updated

@router.post("/{draft_id}/score", response_model=BuyerIntentScoringBreakdown)
def score_post_draft(draft_id: int):
    draft = crud.get_post_draft_by_id(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    text = draft.get("final_edited_content") or draft.get("problem_solution_draft") or ""
    score = scoring_engine.evaluate_draft(
        draft_text=text,
        target_audience=draft.get("target_audience") or "",
        product_key=draft.get("product_key") or ""
    )
    
    crud.update_post_draft(draft_id, {
        "buyer_score_total": score.total_score,
        "buyer_score_breakdown": score.model_dump()
    })
    return score

@router.post("/{draft_id}/feedback")
def submit_voice_feedback(draft_id: int, feedback_tag: str = Query(...)):
    draft = crud.get_post_draft_by_id(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    updated_profile = voice_engine.record_feedback(draft_id, feedback_tag)
    return {"success": True, "feedback_tag": feedback_tag, "updated_voice_profile": updated_profile}
