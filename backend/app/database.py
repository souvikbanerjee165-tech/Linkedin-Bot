import sqlite3
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator
from app.config import settings

def get_db_path() -> Path:
    p = Path(settings.database_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Profile Brand table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profile_brand (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        linkedin_url TEXT,
        headline TEXT,
        about_text TEXT,
        experience_summary TEXT,
        skills TEXT,
        featured_projects TEXT,
        current_services TEXT,
        target_markets TEXT,
        ideal_client_profile TEXT,
        topics_to_discuss TEXT,
        topics_to_avoid TEXT,
        selected_positioning TEXT DEFAULT 'A',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Knowledge items table (5-tier distinction)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL CHECK(category IN ('verified_fact', 'personal_opinion', 'reasonable_interpretation', 'unverified_hypothesis', 'needs_approval')),
        title TEXT NOT NULL,
        claim_content TEXT NOT NULL,
        evidence_source TEXT,
        tags TEXT,
        is_verified INTEGER DEFAULT 0,
        approved_by_user INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_key TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        tagline TEXT,
        description TEXT NOT NULL,
        target_audience TEXT,
        verified_capabilities TEXT,
        concept_capabilities TEXT,
        metrics_case_studies TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Writing samples and voice profile
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS writing_samples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT NOT NULL,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS voice_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        typical_sentence_length REAL DEFAULT 14.5,
        formality_level REAL DEFAULT 0.45,
        technical_depth REAL DEFAULT 0.65,
        directness_confidence REAL DEFAULT 0.85,
        humor_level REAL DEFAULT 0.20,
        storytelling_style TEXT,
        vocabulary_phrasing TEXT,
        stylistic_habits TEXT,
        voice_match_default REAL DEFAULT 0.80,
        feedback_history TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. Content calendar
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS content_calendar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheduled_date TEXT NOT NULL,
        day_number INTEGER,
        target_reader TEXT,
        pain_point TEXT,
        pillar_id INTEGER,
        pillar_name TEXT,
        hook_idea TEXT,
        core_argument TEXT,
        evidence_needed TEXT,
        intended_response TEXT,
        recommended_format TEXT,
        commercial_intent TEXT,
        product_key TEXT,
        status TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'drafted', 'approved', 'published', 'skipped')),
        draft_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. Post drafts & revisions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS post_drafts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        idea_prompt TEXT NOT NULL,
        product_key TEXT,
        target_audience TEXT,
        content_pillar TEXT,
        voice_match_level REAL DEFAULT 0.80,
        active_draft_format TEXT DEFAULT 'problem_solution',
        concise_draft TEXT,
        story_draft TEXT,
        problem_solution_draft TEXT,
        technical_breakdown_draft TEXT,
        demo_draft TEXT,
        commercial_draft TEXT,
        metadata_json TEXT,
        final_edited_content TEXT,
        buyer_score_total INTEGER,
        buyer_score_breakdown TEXT,
        claims_flagged TEXT,
        visual_suggestion TEXT,
        feedback_tag TEXT,
        status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'review_ready', 'approved', 'published', 'archived')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. Research items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS research_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        source_url TEXT,
        source_type TEXT DEFAULT 'article',
        raw_excerpt TEXT,
        analyst_notes TEXT,
        synthesized_problems TEXT,
        buyer_questions TEXT,
        industry_vocabulary TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 8. Post performance metrics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS post_performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_draft_id INTEGER,
        post_title TEXT,
        published_date TEXT,
        period_type TEXT DEFAULT '24h' CHECK(period_type IN ('24h', '7d', '30d', 'custom')),
        impressions INTEGER DEFAULT 0,
        reactions INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        reposts INTEGER DEFAULT 0,
        profile_visits INTEGER DEFAULT 0,
        connection_requests INTEGER DEFAULT 0,
        inbound_dms INTEGER DEFAULT 0,
        qualified_leads INTEGER DEFAULT 0,
        sales_opportunities INTEGER DEFAULT 0,
        revenue_attributed REAL DEFAULT 0.0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_draft_id) REFERENCES post_drafts(id) ON DELETE SET NULL
    );
    """)

    # 9. API usage and cost log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        endpoint TEXT NOT NULL,
        model TEXT NOT NULL,
        prompt_tokens INTEGER DEFAULT 0,
        completion_tokens INTEGER DEFAULT 0,
        total_tokens INTEGER DEFAULT 0,
        estimated_cost_usd REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

def seed_initial_data_if_empty():
    conn = get_connection()
    cursor = conn.cursor()

    # Check products
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        initial_products = [
            (
                "podleads_ai",
                "PodLeads AI",
                "YouTube Lead Generation & Sales Intelligence",
                "A YouTube lead-generation and sales-intelligence system for video-editing agencies, YouTube consultants, podcast repurposing agencies, and content service providers. Helps identify potential clients, analyze content opportunities, prioritize prospects, create personalized outreach, and organize follow-ups.",
                "Video-editing agencies, YouTube consultants, podcast repurposing agencies, content marketing agencies",
                json.dumps([
                    "Prospect channel identification and metadata extraction",
                    "Content opportunity gap analysis",
                    "Personalized outreach message framework",
                    "Pipeline organization and status tracking"
                ]),
                json.dumps([
                    "Automated live CRM sync (Concept / In roadmap)",
                    "Multimodal thumbnail performance scoring (Concept)"
                ]),
                "Tested on active prospective agency accounts with positive engagement on targeted outreach."
            ),
            (
                "dental_sales_intel",
                "Dental Sales Intelligence",
                "Public Signal Research & Opportunity Discovery for Dental Practices",
                "A system for researching dental practices, analyzing publicly observable digital signals, identifying potential growth opportunities, prioritizing prospects, and assisting sales outreach. Examines website technology, online presence, booking functionality, and observable business signals.",
                "Dental marketing agencies, healthcare consultancies, B2B dental SaaS reps",
                json.dumps([
                    "Public dental website technology inspection",
                    "Observable online booking capability detection",
                    "Local presence and public contact point verification",
                    "Structured opportunity briefing generation for outreach"
                ]),
                json.dumps([
                    "Direct practice management software EHR integration (Concept)",
                    "Automated phone system audit (Concept)"
                ]),
                "Provides structured digital audits for sales reps targeting dental clinics."
            ),
            (
                "dental_os_front_desk",
                "Dental Operating System & AI Front Desk",
                "AI-Powered Operations & Front-Desk Workflow System (Concept)",
                "An AI-powered business operations concept for dental practices. Potential capabilities include answering inquiries, assisting with appointment workflows, following up on missed calls, managing recalls, and supporting front-desk processes.",
                "Dental practice owners, clinic managers, group dental practices",
                json.dumps([
                    "Architectural concept and workflow sequence design",
                    "Prototype simulated patient inquiry triage"
                ]),
                json.dumps([
                    "Live VoIP telephone front-desk answering (In design / Concept)",
                    "Direct HIPAA-compliant calendar auto-booking (In design / Concept)",
                    "Automated patient recall SMS pipeline (In design / Concept)"
                ]),
                "Currently in concept & prototype phase. Implementation status must be verified before marketing live operational figures."
            )
        ]
        cursor.executemany("""
        INSERT INTO products (
            product_key, name, tagline, description, target_audience,
            verified_capabilities, concept_capabilities, metrics_case_studies
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, initial_products)

    # Check profile brand
    cursor.execute("SELECT COUNT(*) FROM profile_brand")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO profile_brand (
            headline, about_text, experience_summary, skills, current_services,
            target_markets, ideal_client_profile, topics_to_discuss, topics_to_avoid, selected_positioning
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Building AI-Powered Business Systems & Sales Intelligence That Solve Real Operational Bottlenecks",
            "I am a self-taught software builder, automation specialist, video editor, and digital marketer. I design and build AI-powered software systems that solve practical business problems — from lead generation intelligence to operational workflow automation.",
            "Built PodLeads AI for content agencies, Dental Sales Intelligence for healthcare outreach, and automated internal workflows for client lead pipelines.",
            "AI Automation, Python, FastAPI, React, Sales Intelligence, Workflow Architecture, Content Systems, Video Editing, B2B Positioning",
            "Custom AI business automation, sales intelligence tooling, custom web applications, workflow architecture consulting",
            "United States, Canada, United Kingdom, Australia",
            "Agency founders, B2B business owners, healthcare/dental practice leaders seeking tangible workflow automation rather than hype",
            "Practical AI demonstrations, software architecture lessons, concrete business bottlenecks, workflow before-and-after breakdowns",
            "Generic AI hype ('AI will replace everyone'), fake revenue bragging, fabricated testimonials, engagement bait",
            "A"
        ))

    # Check voice profile
    cursor.execute("SELECT COUNT(*) FROM voice_profile")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO voice_profile (
            typical_sentence_length, formality_level, technical_depth,
            directness_confidence, humor_level, storytelling_style,
            vocabulary_phrasing, stylistic_habits, voice_match_default
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            14.2, 0.40, 0.70, 0.85, 0.20,
            "Direct builder perspective: begins with a real operational obstacle, shows what was built, explains the trade-off, closes with clear principle.",
            "Pragmatic, technical yet plainspoken. Uses terms like 'pipeline', 'signal', 'operational bottleneck', 'friction point', 'tactical'. Avoids corporate buzzwords like 'synergy', 'game-changer', 'revolutionize'.",
            "Short punchy paragraphs, concrete problem definitions, zero generic motivational quotes.",
            0.85
        ))

    # Check initial verified knowledge items
    cursor.execute("SELECT COUNT(*) FROM knowledge_items")
    if cursor.fetchone()[0] == 0:
        initial_claims = [
            (
                "verified_fact",
                "Core Background",
                "Self-taught software builder, automation specialist, video editor, and digital marketer with multi-disciplinary execution experience.",
                "Personal bio & verified skills",
                "background, skills",
                1, 1
            ),
            (
                "verified_fact",
                "Product: PodLeads AI",
                "PodLeads AI identifies YouTube creator opportunities and formats structured sales intelligence for video-editing and repurposing agencies.",
                "PodLeads AI source repository & prototype",
                "podleads_ai, lead_gen",
                1, 1
            ),
            (
                "verified_fact",
                "Product: Dental Sales Intelligence",
                "Dental Sales Intelligence extracts publicly observable signals (website tech, booking presence) to uncover growth bottlenecks for dental outreach.",
                "Dental Sales Intelligence codebase",
                "dental, sales_intelligence",
                1, 1
            ),
            (
                "unverified_hypothesis",
                "Dental Operating System Deployment",
                "Autonomous AI front-desk call handling can eliminate 40% of missed dental front-desk booking inquiries.",
                "Market operational estimate - requires live clinic validation trial",
                "dental_os, hypothesis",
                0, 0
            ),
            (
                "needs_approval",
                "Client Case Study Metrics",
                "Specific revenue improvements or conversion percentages claimed for clients must be validated by the user before publication.",
                "Internal audit policy",
                "governance, compliance",
                0, 0
            )
        ]
        cursor.executemany("""
        INSERT INTO knowledge_items (
            category, title, claim_content, evidence_source, tags, is_verified, approved_by_user
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, initial_claims)

    conn.commit()
    conn.close()

def create_database_backup() -> str:
    db_path = get_db_path()
    backup_dir = Path(settings.backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"backup_linkedin_copilot_{timestamp}.db"
    shutil.copy2(db_path, backup_file)
    return str(backup_file)

def restore_database_backup(backup_filepath: str) -> bool:
    src = Path(backup_filepath)
    if not src.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_filepath}")
    dst = get_db_path()
    shutil.copy2(src, dst)
    return True
