from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# 1. Profile Brand Schemas
class ProfileBrandBase(BaseModel):
    linkedin_url: Optional[str] = ""
    headline: Optional[str] = ""
    about_text: Optional[str] = ""
    experience_summary: Optional[str] = ""
    skills: Optional[str] = ""
    featured_projects: Optional[str] = ""
    current_services: Optional[str] = ""
    target_markets: Optional[str] = "United States, Canada, United Kingdom, Australia"
    ideal_client_profile: Optional[str] = ""
    topics_to_discuss: Optional[str] = ""
    topics_to_avoid: Optional[str] = ""
    selected_positioning: Optional[str] = "A"

class ProfileBrandUpdate(ProfileBrandBase):
    pass

class ProfileBrandResponse(ProfileBrandBase):
    id: int
    updated_at: Optional[str] = None

# Profile Intelligence Audit Response
class PositioningOption(BaseModel):
    option_key: str  # A, B, C
    title: str
    target_market: str
    primary_value_prop: str
    pros: List[str]
    cons: List[str]
    fit_score: int  # 0 - 100
    recommendation_reason: str

class ProfileAuditCategory(BaseModel):
    category_name: str
    score: int  # 0 - 100
    evidence: str
    strengths: List[str]
    gaps: List[str]
    actionable_fix: str

class ProfileIntelligenceReport(BaseModel):
    overall_score: int
    recommended_positioning: str
    positioning_options: List[PositioningOption]
    category_audits: List[ProfileAuditCategory]
    headline_alternatives: List[Dict[str, str]]
    rewritten_about_section: str
    experience_recommendations: List[str]
    featured_section_actions: List[str]
    service_cta_recommendations: List[str]
    trust_credibility_gaps: List[str]
    buyer_relevance_summary: str

# 2. Knowledge Item Schemas
class KnowledgeItemBase(BaseModel):
    category: str = Field(..., description="verified_fact | personal_opinion | reasonable_interpretation | unverified_hypothesis | needs_approval")
    title: str
    claim_content: str
    evidence_source: Optional[str] = ""
    tags: Optional[str] = ""
    is_verified: bool = False
    approved_by_user: bool = False

class KnowledgeItemCreate(KnowledgeItemBase):
    pass

class KnowledgeItemUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    claim_content: Optional[str] = None
    evidence_source: Optional[str] = None
    tags: Optional[str] = None
    is_verified: Optional[bool] = None
    approved_by_user: Optional[bool] = None

class KnowledgeItemResponse(KnowledgeItemBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# 3. Product Schemas
class ProductBase(BaseModel):
    product_key: str
    name: str
    tagline: Optional[str] = ""
    description: str
    target_audience: Optional[str] = ""
    verified_capabilities: List[str] = []
    concept_capabilities: List[str] = []
    metrics_case_studies: Optional[str] = ""

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    target_audience: Optional[str] = None
    verified_capabilities: Optional[List[str]] = None
    concept_capabilities: Optional[List[str]] = None
    metrics_case_studies: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# 4. Writing Sample & Voice Profile
class WritingSampleCreate(BaseModel):
    title: Optional[str] = "Writing Sample"
    content: str
    source: Optional[str] = "LinkedIn post"

class WritingSampleResponse(BaseModel):
    id: int
    title: Optional[str]
    content: str
    source: Optional[str]
    created_at: Optional[str]

class VoiceProfileUpdate(BaseModel):
    typical_sentence_length: Optional[float] = None
    formality_level: Optional[float] = None
    technical_depth: Optional[float] = None
    directness_confidence: Optional[float] = None
    humor_level: Optional[float] = None
    storytelling_style: Optional[str] = None
    vocabulary_phrasing: Optional[str] = None
    stylistic_habits: Optional[str] = None
    voice_match_default: Optional[float] = None

class VoiceProfileResponse(BaseModel):
    id: int
    typical_sentence_length: float
    formality_level: float
    technical_depth: float
    directness_confidence: float
    humor_level: float
    storytelling_style: Optional[str]
    vocabulary_phrasing: Optional[str]
    stylistic_habits: Optional[str]
    voice_match_default: float
    feedback_history: Optional[str]
    updated_at: Optional[str]

# 5. Content Calendar Schemas
class CalendarItemBase(BaseModel):
    scheduled_date: str
    day_number: Optional[int] = None
    target_reader: str
    pain_point: str
    pillar_id: int
    pillar_name: str
    hook_idea: str
    core_argument: str
    evidence_needed: Optional[str] = ""
    intended_response: Optional[str] = ""
    recommended_format: str
    commercial_intent: Optional[str] = ""
    product_key: Optional[str] = None
    status: str = "scheduled"
    draft_id: Optional[int] = None

class CalendarItemCreate(CalendarItemBase):
    pass

class CalendarItemUpdate(BaseModel):
    scheduled_date: Optional[str] = None
    target_reader: Optional[str] = None
    pain_point: Optional[str] = None
    pillar_id: Optional[int] = None
    pillar_name: Optional[str] = None
    hook_idea: Optional[str] = None
    core_argument: Optional[str] = None
    evidence_needed: Optional[str] = None
    intended_response: Optional[str] = None
    recommended_format: Optional[str] = None
    commercial_intent: Optional[str] = None
    product_key: Optional[str] = None
    status: Optional[str] = None
    draft_id: Optional[int] = None

class CalendarItemResponse(CalendarItemBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class GenerateCalendarRequest(BaseModel):
    days_count: int = Field(default=7, description="7 or 30 days")
    start_date: Optional[str] = None
    target_product_key: Optional[str] = None
    primary_focus_pillar: Optional[int] = None

# 6. Post Generation & Scoring Schemas
class PostGenerateRequest(BaseModel):
    idea_prompt: str
    product_key: Optional[str] = "podleads_ai"
    target_audience: Optional[str] = "Agency Founders & B2B Decision Makers"
    content_pillar: Optional[int] = 1
    voice_match_level: Optional[float] = 0.85
    commercial_intent: Optional[str] = "Demonstrate capability and spark inbound conversation"
    additional_context: Optional[str] = ""

class DraftFormatOutput(BaseModel):
    format_type: str  # concise | story | problem_solution | technical_breakdown | demo | commercial
    title: str
    hook: str
    main_body: str
    closing_line: str
    call_to_action: Optional[str]
    target_audience: str
    primary_purpose: str
    claims_to_verify: List[str]
    suggested_visual: str
    full_text: str

class PostGenerateResponse(BaseModel):
    draft_id: int
    idea_prompt: str
    product_key: Optional[str]
    drafts: Dict[str, DraftFormatOutput]
    claims_flagged: List[str]
    token_usage: Dict[str, Any]
    estimated_cost_usd: float

class BuyerIntentScoringBreakdown(BaseModel):
    audience_relevance: int = Field(..., ge=0, le=20)
    problem_specificity: int = Field(..., ge=0, le=20)
    evidence_credibility: int = Field(..., ge=0, le=20)
    originality_usefulness: int = Field(..., ge=0, le=15)
    readability: int = Field(..., ge=0, le=10)
    commercial_relevance: int = Field(..., ge=0, le=10)
    cta_quality: int = Field(..., ge=0, le=5)
    total_score: int = Field(..., ge=0, le=100)
    scoring_rationale: Dict[str, str]
    actionable_improvements: List[str]
    viral_disclaimer: str = "Editorial heuristics for B2B buyer clarity; not algorithmic reach predictions."

class PostDraftUpdate(BaseModel):
    active_draft_format: Optional[str] = None
    final_edited_content: Optional[str] = None
    status: Optional[str] = None
    feedback_tag: Optional[str] = None

class PostDraftResponse(BaseModel):
    id: int
    idea_prompt: str
    product_key: Optional[str]
    target_audience: Optional[str]
    content_pillar: Optional[str]
    voice_match_level: float
    active_draft_format: str
    concise_draft: Optional[str]
    story_draft: Optional[str]
    problem_solution_draft: Optional[str]
    technical_breakdown_draft: Optional[str]
    demo_draft: Optional[str]
    commercial_draft: Optional[str]
    final_edited_content: Optional[str]
    buyer_score_total: Optional[int]
    buyer_score_breakdown: Optional[Dict[str, Any]]
    claims_flagged: Optional[List[str]]
    visual_suggestion: Optional[str]
    feedback_tag: Optional[str]
    status: str
    created_at: Optional[str]
    updated_at: Optional[str]

# 7. Research Schemas
class ResearchItemBase(BaseModel):
    title: str
    source_url: Optional[str] = ""
    source_type: Optional[str] = "article"
    raw_excerpt: Optional[str] = ""
    analyst_notes: Optional[str] = ""
    synthesized_problems: Optional[str] = ""
    buyer_questions: Optional[str] = ""
    industry_vocabulary: Optional[str] = ""
    tags: Optional[str] = ""

class ResearchItemCreate(ResearchItemBase):
    pass

class ResearchItemResponse(ResearchItemBase):
    id: int
    created_at: Optional[str]

# 8. Post Performance Schemas
class PerformanceLogCreate(BaseModel):
    post_draft_id: Optional[int] = None
    post_title: str
    published_date: str
    period_type: str = "24h"
    impressions: int = 0
    reactions: int = 0
    comments: int = 0
    reposts: int = 0
    profile_visits: int = 0
    connection_requests: int = 0
    inbound_dms: int = 0
    qualified_leads: int = 0
    sales_opportunities: int = 0
    revenue_attributed: float = 0.0
    notes: Optional[str] = ""

class PerformanceLogResponse(PerformanceLogCreate):
    id: int
    created_at: Optional[str]
    updated_at: Optional[str]

class PerformanceAnalyticsSummary(BaseModel):
    total_posts_tracked: int
    total_impressions: int
    total_reactions: int
    total_comments: int
    total_inbound_dms: int
    total_qualified_leads: int
    total_sales_opportunities: int
    total_revenue_attributed: float
    lead_conversion_rate: float
    opportunity_rate: float
    best_performing_formats: List[Dict[str, Any]]
    best_performing_pillars: List[Dict[str, Any]]
    recommended_experiments: List[str]

# 9. System & Usage Schemas
class ApiUsageSummary(BaseModel):
    total_calls: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    total_cost_usd: float
    is_api_key_configured: bool
    current_model: str
