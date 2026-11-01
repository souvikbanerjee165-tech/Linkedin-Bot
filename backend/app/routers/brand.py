from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
import json
import logging
from app import crud
from app.config import settings
from app.schemas import ProfileBrandResponse, ProfileBrandUpdate, ProfileIntelligenceReport, PositioningOption, ProfileAuditCategory
from app.services.deepseek_client import deepseek_client

logger = logging.getLogger("brand_router")
router = APIRouter(prefix="/api/brand", tags=["Brand"])

@router.get("", response_model=ProfileBrandResponse)
def get_brand():
    brand = crud.get_profile_brand()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not initialized")
    return brand

@router.post("", response_model=ProfileBrandResponse)
def update_brand(payload: ProfileBrandUpdate):
    updated = crud.update_profile_brand(payload.model_dump(exclude_unset=True))
    return updated

@router.get("/audit", response_model=ProfileIntelligenceReport)
async def get_profile_audit(use_ai: bool = Query(False, description="Run live DeepSeek profile audit using current brand & knowledge")):
    brand = crud.get_profile_brand() or {}
    products = crud.get_products()
    knowledge_items = crud.get_knowledge_items()
    
    # 3 Positioning Options
    positioning_options = [
        PositioningOption(
            option_key="A",
            title="AI Automation & Custom Business Systems Builder",
            target_market="Agency founders, digital businesses, and operational leaders needing bespoke automation pipelines.",
            primary_value_prop="I design and build end-to-end custom software and AI workflows that remove operational bottlenecks and cut manual labor.",
            pros=[
                "Directly showcases hands-on software development and automation capabilities",
                "Broad addressable market across service businesses and digital agencies",
                "Highest pricing power for custom engineering projects"
            ],
            cons=[
                "Broader scope requires strong qualification to avoid small low-budget clients",
                "Must clearly differentiate from generic 'no-code Zapier' freelancers"
            ],
            fit_score=92,
            recommendation_reason="Strongest fit for your multifaceted background across full-stack software, workflow design, video tools, and practical execution."
        ),
        PositioningOption(
            option_key="B",
            title="B2B Sales Intelligence & Lead-Generation Systems Specialist",
            target_market="B2B sales teams, outbound agencies, and growth-stage consultancies.",
            primary_value_prop="I build custom data intelligence pipelines (like PodLeads AI) that extract observable signals to identify high-converting prospects.",
            pros=[
                "High commercial urgency: directly tied to top-of-funnel revenue and leads",
                "PodLeads AI provides an immediate working demonstration of capability"
            ],
            cons=[
                "Narrows your positioning away from broader internal operations and custom tools"
            ],
            fit_score=85,
            recommendation_reason="Excellent secondary angle or specialized focus for content targeting agencies and outbound sales leaders."
        ),
        PositioningOption(
            option_key="C",
            title="AI Workflow Consultant for Specialized Vertical (Dental/Healthcare)",
            target_market="Dental practice owners, clinic managers, and healthcare service groups.",
            primary_value_prop="I help dental practices uncover growth opportunities from public digital signals and design front-desk operational workflows.",
            pros=[
                "Highly specific niche with clear industry language and pain points",
                "Dental Sales Intelligence is purpose-built for this sector"
            ],
            cons=[
                "Dental Operating System & AI Front Desk is currently in concept/prototype stage; claims must be carefully gated to avoid over-promising live clinic results."
            ],
            fit_score=78,
            recommendation_reason="High long-term commercial upside, but best run as a targeted industry vertical rather than restricting your entire personal profile."
        )
    ]

    # Category Audits
    category_audits = [
        ProfileAuditCategory(
            category_name="Positioning & Differentiation",
            score=88,
            evidence="Profile clearly highlights technical builder capabilities and practical problem-solving rather than generic hype.",
            strengths=["Clear rejection of buzzwords", "Focus on practical systems over generic influencer claims"],
            gaps=["Headline can more aggressively emphasize commercial ROI and specific client bottlenecks"],
            actionable_fix="Specify the exact scale of operational bottlenecks solved in the headline."
        ),
        ProfileAuditCategory(
            category_name="Buyer Relevance & Trust Gaps",
            score=84,
            evidence="Demonstrates three tangible software concepts with transparent distinction between live features and concepts.",
            strengths=["Grounded technical vocabulary", "PodLeads AI provides concrete agency relevance"],
            gaps=["Needs prominent featured links to live walkthroughs or architecture teardowns"],
            actionable_fix="Add 2 featured posts detailing architecture lessons from building PodLeads AI."
        ),
        ProfileAuditCategory(
            category_name="Headline & About Section Impact",
            score=86,
            evidence="About section articulates personal trajectory and multi-disciplinary capability well.",
            strengths=["Authentic voice", "Clear statement of services offered"],
            gaps=["Can include a more direct, low-friction invitation for business owners to start a conversation"],
            actionable_fix="Add an explicit 'How to work together' paragraph at the bottom of the About section."
        )
    ]

    headline_alternatives = [
        {
            "angle": "Option A: Systems Builder (Recommended)",
            "headline": "Building AI-Powered Business Systems & Sales Intelligence That Eliminate Operational Bottlenecks | Custom Software & Workflow Architecture"
        },
        {
            "angle": "Option B: Sales Intelligence Specialist",
            "headline": "Creator of PodLeads AI | Building Custom Sales Intelligence & Signal Discovery Systems for B2B Agencies & High-Growth Teams"
        },
        {
            "angle": "Option C: Pragmatic Problem Solver",
            "headline": "Software Builder & Automation Specialist | Designing AI Systems That Solve Real Business Problems (Without the Hype)"
        }
    ]

    rewritten_about = (
        "Most businesses don't need another generic AI chatbot or a 50-step Zapier sequence that breaks every Tuesday.\n\n"
        "They need reliable software systems that solve specific operational headaches: qualifying prospects before outreach, organizing messy workflows, and removing manual data friction.\n\n"
        "I am a self-taught software builder and automation specialist. I build AI-powered applications and sales intelligence tools that solve concrete business problems:\n\n"
        "• PodLeads AI: YouTube sales intelligence for video agencies and repurposing studios.\n"
        "• Dental Sales Intelligence: Observable digital signal discovery for healthcare outreach.\n"
        "• Custom Business Systems: Automated workflows, internal tools, and client data pipelines.\n\n"
        "My philosophy: Test observable signals first, automate the bottleneck second, and never confuse language models with verifiable business facts.\n\n"
        "If your team is losing 10+ hours a week to manual workflow drag, send me a message or connect. Let's look at the bottleneck."
    )

    overall_score = 86
    recommended_positioning = "Option A: AI Automation & Custom Business Systems Builder"
    buyer_relevance_summary = "Your profile establishes high credibility by combining actual software engineering capability with grounded commercial awareness. Recommending Option A gives you the widest commercial foundation while leveraging your specialized products as tangible proof."

    if use_ai and settings.is_api_key_configured:
        try:
            verified_facts = [f"{k['title']}: {k['claim_content']}" for k in knowledge_items if k.get("category") == "verified_fact"]
            product_summaries = [f"{p['name']} ({p['tagline']}): Verified={p['verified_capabilities']}, Concept={p['concept_capabilities']}" for p in products]
            sys_prompt = (
                "You are a principal B2B LinkedIn positioning strategist. Analyze the user's current brand profile, "
                "verified knowledge base, and software products. Never invent clients, revenue, or live case studies.\n"
                "Return a valid JSON object containing:\n"
                "- overall_score (integer 60-98)\n"
                "- recommended_positioning (string)\n"
                "- rewritten_about_section (string, 3-5 punchy paragraphs)\n"
                "- headline_alternatives (list of 3 dicts with 'angle' and 'headline')\n"
                "- buyer_relevance_summary (string)\n"
            )
            usr_prompt = (
                f"Current Headline: {brand.get('headline')}\n"
                f"Current About: {brand.get('about_text')}\n"
                f"Experience: {brand.get('experience_summary')}\n"
                f"Services: {brand.get('current_services')}\n"
                f"Target Markets: {brand.get('target_markets')}\n"
                f"Ideal Client: {brand.get('ideal_client_profile')}\n"
                f"Products: {'; '.join(product_summaries)}\n"
                f"Verified Facts: {'; '.join(verified_facts)}\n"
                "Generate the tailored JSON profile audit report."
            )
            completion = await deepseek_client.call_completion(
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": usr_prompt}
                ],
                temperature=0.6,
                response_format={"type": "json_object"},
                endpoint_name="brand_profile_audit"
            )
            raw = completion["content"].strip()
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                overall_score = int(parsed.get("overall_score") or overall_score)
                recommended_positioning = parsed.get("recommended_positioning") or recommended_positioning
                rewritten_about = parsed.get("rewritten_about_section") or rewritten_about
                if isinstance(parsed.get("headline_alternatives"), list) and len(parsed["headline_alternatives"]) > 0:
                    headline_alternatives = [
                        {"angle": str(h.get("angle", "Alternative")), "headline": str(h.get("headline", ""))}
                        for h in parsed["headline_alternatives"] if isinstance(h, dict) and h.get("headline")
                    ] or headline_alternatives
                buyer_relevance_summary = parsed.get("buyer_relevance_summary") or buyer_relevance_summary
        except Exception as exc:
            logger.warning(f"AI brand audit fallback triggered: {exc}")

    return ProfileIntelligenceReport(
        overall_score=overall_score,
        recommended_positioning=recommended_positioning,
        positioning_options=positioning_options,
        category_audits=category_audits,
        headline_alternatives=headline_alternatives,
        rewritten_about_section=rewritten_about,
        experience_recommendations=[
            "Structure experience entries around 'Problem -> System Built -> Measurable Friction Eliminated'.",
            "Explicitly list technical stack (Python, FastAPI, SQLite, React, HTTPX, APIs) alongside business outcomes.",
            "Include links to live demo recordings or code architecture summaries."
        ],
        featured_section_actions=[
            "Feature 1: Interactive walkthrough or architecture breakdown of PodLeads AI.",
            "Feature 2: Case breakdown of observable digital signals for dental practices.",
            "Feature 3: A contrarian post on why businesses should fix manual workflow bottlenecks before buying AI."
        ],
        service_cta_recommendations=[
            "Low-friction call to action: 'Direct message me AUDIT for a 10-minute bottleneck breakdown.'",
            "Offer a 3-point observable signal analysis for prospective agency partners."
        ],
        trust_credibility_gaps=[
            "Ensure concept features in Dental OS are clearly demarcated from live verified tools.",
            "Avoid sharing theoretical revenue projections without verified customer confirmation."
        ],
        buyer_relevance_summary=buyer_relevance_summary
    )
