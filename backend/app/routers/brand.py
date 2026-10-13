from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app import crud
from app.schemas import ProfileBrandResponse, ProfileBrandUpdate, ProfileIntelligenceReport, PositioningOption, ProfileAuditCategory

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
def get_profile_audit():
    brand = crud.get_profile_brand() or {}
    products = crud.get_products()
    
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

    return ProfileIntelligenceReport(
        overall_score=86,
        recommended_positioning="Option A: AI Automation & Custom Business Systems Builder",
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
        buyer_relevance_summary="Your profile establishes high credibility by combining actual software engineering capability with grounded commercial awareness. Recommending Option A gives you the widest commercial foundation while leveraging your specialized products as tangible proof."
    )
