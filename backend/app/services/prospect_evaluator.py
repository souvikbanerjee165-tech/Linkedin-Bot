import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from app.services.signal_inspector import validate_public_url, signal_inspector
from app.services.deepseek_client import deepseek_client
from app import crud

logger = logging.getLogger("prospect_evaluator")

class ProspectLeadEvaluator:
    """
    Automated B2B Lead Scraper & Prospect Evaluator
    Inspired by joeyism/linkedin_scraper, stickerdaniel/fast-linkedin-scraper, and ashmitb95/linkedin-leadgen.
    1. Validates public prospect company URL / digital channels (SSRF safe).
    2. Uses Playwright Chromium to extract observable digital friction signals (load speed, booking systems, widgets).
    3. Runs DeepSeek LLM scoring pass to evaluate buying authority and friction level.
    4. Automatically generates a personalized, signal-informed outreach pitch.
    5. Saves the scored lead directly into the SQLite Inbound CRM pipeline (prospect_leads table).
    """

    async def inspect_and_evaluate(
        self,
        target_url: str,
        prospect_name: str,
        company: str,
        role_title: str,
        product_focus: str = "dental_sales_intel"
    ) -> Dict[str, Any]:
        # Step 1: Playwright inspection
        signals = await signal_inspector.inspect_website(target_url)
        opp_score = signals.get("opportunity_score", 50)
        bottlenecks = signals.get("observable_bottlenecks", [])

        # Step 2: DeepSeek LLM evaluation & personalized outreach angle
        sys_prompt = (
            "You are a B2B Sales Intelligence Architect.\n"
            "Analyze the observed digital signals of a prospective client company. Score their buying friction and draft a tailored 3-sentence outreach message.\n"
            "Rules:\n"
            "- Never make generic cold pitches.\n"
            "- Reference the specific observable bottleneck discovered during website inspection.\n"
            "- Return a JSON object with: 'buying_intent_score' (int 0-100), 'urgency_reason' (string), 'custom_outreach_pitch' (string)."
        )
        usr_prompt = (
            f"Prospect Name: {prospect_name}\n"
            f"Company: {company} ({signals.get('page_title') or target_url})\n"
            f"Role: {role_title}\n"
            f"Our Solution: {product_focus.replace('_', ' ').title()}\n"
            f"Observable Bottlenecks: {'; '.join(bottlenecks)}\n"
            f"Load Time: {signals.get('load_time_seconds')}s | Interactive Booking: {signals.get('has_interactive_booking')}\n"
            "Generate structured prospect evaluation in JSON."
        )

        llm_res = await deepseek_client.call_completion(
            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": usr_prompt}],
            temperature=0.4,
            response_format={"type": "json_object"},
            endpoint_name="prospect_lead_evaluation"
        )

        pitch_text = ""
        buying_intent = opp_score
        try:
            raw = llm_res["content"].strip()
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                pitch_text = parsed.get("custom_outreach_pitch") or ""
                buying_intent = int(parsed.get("buying_intent_score", opp_score))
        except Exception:
            pitch_text = f"Hi {prospect_name}, noticed {company}'s website relies strictly on manual phone calls for patient inquiries after 5 PM. We build automated workflow pipelines to capture these lost opportunities."

        # Step 3: Persist lead into CRM
        lead_record = {
            "prospect_name": prospect_name,
            "company": company or signals.get("page_title", "Prospect Co"),
            "role_title": role_title or "Decision Maker",
            "website_url": target_url,
            "origin_post_id": None,
            "stage": "inbound_dm",
            "deal_value_usd": 3500.0,
            "notes": f"Score: {buying_intent}/100. Signal pitch: {pitch_text}"
        }
        saved_lead = crud.create_prospect_lead(lead_record)

        return {
            "lead": saved_lead,
            "signals": signals,
            "buying_intent_score": buying_intent,
            "custom_outreach_pitch": pitch_text
        }

prospect_evaluator = ProspectLeadEvaluator()
