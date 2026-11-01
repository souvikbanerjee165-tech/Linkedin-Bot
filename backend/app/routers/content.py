from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import json
import logging
from app import crud
from app.config import settings
from app.schemas import (
    CalendarItemResponse, CalendarItemCreate, CalendarItemUpdate, GenerateCalendarRequest
)
from app.services.deepseek_client import deepseek_client

logger = logging.getLogger("content_router")
router = APIRouter(prefix="/api/calendar", tags=["Content Calendar"])

PILLARS_CATALOG = [
    {
        "id": 1,
        "name": "Business problems that cost companies time or opportunities",
        "format": "problem_solution",
        "hook_template": "Why {audience} lose {hours} every week to manual data sorting.",
        "intent": "Highlight operational friction that custom software fixes"
    },
    {
        "id": 2,
        "name": "Practical AI automation demonstrations",
        "format": "demo",
        "hook_template": "Here is what happens when we run 50 prospective accounts through our inspection pipeline.",
        "intent": "Show tangible output without buzzwords"
    },
    {
        "id": 3,
        "name": "Behind-the-scenes software building and lessons learned",
        "format": "story",
        "hook_template": "Why I scrapped our first version of {product} after 3 weeks of testing.",
        "intent": "Establish technical authenticity and builder credibility"
    },
    {
        "id": 4,
        "name": "Before-and-after workflow comparisons",
        "format": "concise",
        "hook_template": "Before: 4 hours of scraping. After: 30 seconds of structured signal extraction.",
        "intent": "Make the leverage of custom tooling obvious"
    },
    {
        "id": 5,
        "name": "Industry-specific insights (Agency / Healthcare)",
        "format": "problem_solution",
        "hook_template": "The single biggest digital leak in local dental practices (and why it's not SEO).",
        "intent": "Demonstrate deep vertical domain understanding"
    },
    {
        "id": 6,
        "name": "Technical explanations made accessible to business owners",
        "format": "technical_breakdown",
        "hook_template": "Deterministic code vs Language models: When to use which in your business pipeline.",
        "intent": "Position as a trusted technical advisor"
    },
    {
        "id": 7,
        "name": "Mistakes, trade-offs, and lessons from implementation",
        "format": "story",
        "hook_template": "The hidden cost of connecting 15 third-party SaaS tools instead of building one clean script.",
        "intent": "Guide buyers away from fragile no-code traps"
    },
    {
        "id": 8,
        "name": "Case studies based on verified evidence",
        "format": "demo",
        "hook_template": "How signal-based prospecting changed the response rate for targeted video agencies.",
        "intent": "Provide verified proof of concept"
    },
    {
        "id": 9,
        "name": "Contrarian but defensible opinions",
        "format": "concise",
        "hook_template": "Stop buying AI tools before you have audited your manual bottleneck.",
        "intent": "Stand out from AI hype mongers"
    },
    {
        "id": 10,
        "name": "Soft commercial posts that explain what I build and who it helps",
        "format": "commercial",
        "hook_template": "Opening 2 implementation spots for agencies looking to automate prospect discovery next month.",
        "intent": "Direct commercial conversion and inbound DMs"
    }
]

@router.get("", response_model=List[CalendarItemResponse])
def get_calendar():
    return crud.get_calendar_items()

@router.post("/generate", response_model=List[CalendarItemResponse])
async def generate_calendar(payload: GenerateCalendarRequest):
    days = max(7, min(30, payload.days_count))
    crud.clear_calendar_items()

    research_items = crud.get_research_items()
    products = crud.get_products()
    product_keys = [p["product_key"] for p in products] or ["podleads_ai", "dental_sales_intel"]

    today = datetime.now(timezone.utc)
    calendar_entries = []

    ai_items_map = {}
    if payload.use_ai and settings.is_api_key_configured:
        try:
            research_digest = "; ".join([
                f"{r.get('title')}: {r.get('synthesized_problems') or r.get('analyst_notes')}"
                for r in research_items[:6]
            ]) or "General B2B workflow bottlenecks and signal-based sales intelligence."
            sys_prompt = (
                "You are a B2B LinkedIn content strategist. Generate a structured content calendar in JSON format.\n"
                "Return a JSON object with key 'items' containing a list of objects, each with:\n"
                "'day_number' (int), 'target_reader' (str), 'pain_point' (str), 'hook_idea' (str), "
                "'core_argument' (str), 'recommended_format' (one of concise, story, problem_solution, technical_breakdown, demo, commercial)."
            )
            usr_prompt = (
                f"Generate {days} calendar entries grounded in our products ({', '.join(product_keys)}) "
                f"and recent research findings: {research_digest}. Return valid JSON."
            )
            completion = await deepseek_client.call_completion(
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": usr_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
                endpoint_name="calendar_generation"
            )
            raw = completion["content"].strip()
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(raw)
            if isinstance(parsed, dict) and isinstance(parsed.get("items"), list):
                for idx, item in enumerate(parsed["items"]):
                    if isinstance(item, dict):
                        ai_items_map[idx] = item
        except Exception as exc:
            logger.warning(f"Calendar AI generation fallback triggered: {exc}")

    for day_idx in range(days):
        date_str = (today + timedelta(days=day_idx + 1)).strftime("%Y-%m-%d")
        pillar_spec = PILLARS_CATALOG[day_idx % len(PILLARS_CATALOG)]
        
        target_reader = "Agency Founders & Growth Directors" if day_idx % 2 == 0 else "B2B Business Owners & Dental Practice Leaders"
        product_key = payload.target_product_key or ("podleads_ai" if day_idx % 2 == 0 else "dental_sales_intel")
        product_label = "PodLeads AI" if product_key == "podleads_ai" else "Dental Sales Intelligence"

        # Incorporate saved Research Vault insights when available
        research_note = research_items[day_idx % len(research_items)] if research_items else None
        default_pain = (
            research_note.get("synthesized_problems")
            if research_note and research_note.get("synthesized_problems")
            else f"Wasting manual hours and missing opportunities in operational step #{day_idx + 1}."
        )
        default_hook = pillar_spec["hook_template"].replace("{audience}", target_reader).replace("{hours}", "15 hours").replace("{product}", product_label)
        if research_note and day_idx < len(research_items) and research_note.get("analyst_notes"):
            default_arg = f"{research_note.get('analyst_notes')} Focusing on observable signals and robust architecture produces reliable leverage."
        else:
            default_arg = "Focusing on observable signals and robust architecture produces reliable leverage, whereas superficial AI hacks create technical debt."

        ai_override = ai_items_map.get(day_idx, {})

        entry = {
            "scheduled_date": date_str,
            "day_number": day_idx + 1,
            "target_reader": ai_override.get("target_reader") or target_reader,
            "pain_point": ai_override.get("pain_point") or default_pain,
            "pillar_id": pillar_spec["id"],
            "pillar_name": pillar_spec["name"],
            "hook_idea": ai_override.get("hook_idea") or default_hook,
            "core_argument": ai_override.get("core_argument") or default_arg,
            "evidence_needed": "Architecture snippet, observable signal audit screenshot, or verified benchmark metric.",
            "intended_response": "Reader comments with an operational bottleneck or sends a direct message requesting an audit.",
            "recommended_format": ai_override.get("recommended_format") or pillar_spec["format"],
            "commercial_intent": pillar_spec["intent"],
            "product_key": product_key,
            "status": "scheduled",
            "draft_id": None
        }
        saved = crud.create_calendar_item(entry)
        calendar_entries.append(saved)

    return calendar_entries

@router.put("/{item_id}", response_model=CalendarItemResponse)
def update_calendar_item(item_id: int, payload: CalendarItemUpdate):
    updated = crud.update_calendar_item(item_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Calendar item not found")
    return updated
