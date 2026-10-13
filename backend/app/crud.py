import sqlite3
import json
from typing import List, Optional, Dict, Any
from app.database import get_connection

# 1. Profile Brand CRUD
def get_profile_brand() -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM profile_brand ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_profile_brand(data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    existing = conn.execute("SELECT id FROM profile_brand ORDER BY id DESC LIMIT 1").fetchone()
    
    fields = [
        "linkedin_url", "headline", "about_text", "experience_summary",
        "skills", "featured_projects", "current_services", "target_markets",
        "ideal_client_profile", "topics_to_discuss", "topics_to_avoid", "selected_positioning"
    ]
    
    if existing:
        updates = []
        values = []
        for f in fields:
            if f in data and data[f] is not None:
                updates.append(f"{f} = ?")
                values.append(data[f])
        if updates:
            values.append(existing["id"])
            conn.execute(f"UPDATE profile_brand SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
            conn.commit()
    else:
        cols = []
        vals = []
        placeholders = []
        for f in fields:
            if f in data and data[f] is not None:
                cols.append(f)
                vals.append(data[f])
                placeholders.append("?")
        if cols:
            conn.execute(f"INSERT INTO profile_brand ({', '.join(cols)}) VALUES ({', '.join(placeholders)})", vals)
            conn.commit()
            
    conn.close()
    return get_profile_brand()

# 2. Knowledge Items CRUD
def get_knowledge_items(category: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    if category:
        rows = conn.execute("SELECT * FROM knowledge_items WHERE category = ? ORDER BY id DESC", (category,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM knowledge_items ORDER BY id DESC").fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        d["is_verified"] = bool(d["is_verified"])
        d["approved_by_user"] = bool(d["approved_by_user"])
        results.append(d)
    return results

def get_knowledge_item_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM knowledge_items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["is_verified"] = bool(d["is_verified"])
    d["approved_by_user"] = bool(d["approved_by_user"])
    return d

def create_knowledge_item(item: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO knowledge_items (category, title, claim_content, evidence_source, tags, is_verified, approved_by_user)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        item.get("category"),
        item.get("title"),
        item.get("claim_content"),
        item.get("evidence_source", ""),
        item.get("tags", ""),
        1 if item.get("is_verified") else 0,
        1 if item.get("approved_by_user") else 0
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_knowledge_item_by_id(new_id)

def update_knowledge_item(item_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    set_clauses = []
    values = []
    for k, v in updates.items():
        if v is not None:
            if k in ("is_verified", "approved_by_user"):
                set_clauses.append(f"{k} = ?")
                values.append(1 if v else 0)
            else:
                set_clauses.append(f"{k} = ?")
                values.append(v)
    if set_clauses:
        values.append(item_id)
        conn.execute(f"UPDATE knowledge_items SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
        conn.commit()
    conn.close()
    return get_knowledge_item_by_id(item_id)

def delete_knowledge_item(item_id: int) -> bool:
    conn = get_connection()
    conn.execute("DELETE FROM knowledge_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return True

# 3. Products CRUD
def get_products() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM products ORDER BY id ASC").fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        d["verified_capabilities"] = json.loads(d["verified_capabilities"]) if d.get("verified_capabilities") else []
        d["concept_capabilities"] = json.loads(d["concept_capabilities"]) if d.get("concept_capabilities") else []
        results.append(d)
    return results

def get_product_by_key(product_key: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM products WHERE product_key = ?", (product_key,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["verified_capabilities"] = json.loads(d["verified_capabilities"]) if d.get("verified_capabilities") else []
    d["concept_capabilities"] = json.loads(d["concept_capabilities"]) if d.get("concept_capabilities") else []
    return d

def update_product(product_key: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    set_clauses = []
    values = []
    for k, v in updates.items():
        if v is not None:
            if k in ("verified_capabilities", "concept_capabilities"):
                set_clauses.append(f"{k} = ?")
                values.append(json.dumps(v))
            else:
                set_clauses.append(f"{k} = ?")
                values.append(v)
    if set_clauses:
        values.append(product_key)
        conn.execute(f"UPDATE products SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE product_key = ?", values)
        conn.commit()
    conn.close()
    return get_product_by_key(product_key)

# 4. Voice Profile & Writing Samples
def get_voice_profile() -> Dict[str, Any]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM voice_profile ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "id": 1,
        "typical_sentence_length": 14.5,
        "formality_level": 0.45,
        "technical_depth": 0.65,
        "directness_confidence": 0.85,
        "humor_level": 0.20,
        "storytelling_style": "Builder-first lessons with practical bottlenecks",
        "vocabulary_phrasing": "Pragmatic, direct, operational",
        "stylistic_habits": "Short paragraphs, clear outcomes",
        "voice_match_default": 0.80,
        "feedback_history": ""
    }

def update_voice_profile(updates: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    current = conn.execute("SELECT id FROM voice_profile ORDER BY id DESC LIMIT 1").fetchone()
    if current:
        set_clauses = []
        values = []
        for k, v in updates.items():
            if v is not None:
                set_clauses.append(f"{k} = ?")
                values.append(v)
        if set_clauses:
            values.append(current["id"])
            conn.execute(f"UPDATE voice_profile SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
            conn.commit()
    conn.close()
    return get_voice_profile()

def add_writing_sample(sample: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO writing_samples (title, content, source) VALUES (?, ?, ?)", (
        sample.get("title", "Writing Sample"),
        sample.get("content", ""),
        sample.get("source", "LinkedIn")
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": new_id, **sample}

def get_writing_samples() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM writing_samples ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# 5. Content Calendar CRUD
def get_calendar_items() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM content_calendar ORDER BY scheduled_date ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_calendar_item(item: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO content_calendar (
        scheduled_date, day_number, target_reader, pain_point, pillar_id, pillar_name,
        hook_idea, core_argument, evidence_needed, intended_response, recommended_format,
        commercial_intent, product_key, status, draft_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item.get("scheduled_date"),
        item.get("day_number"),
        item.get("target_reader"),
        item.get("pain_point"),
        item.get("pillar_id"),
        item.get("pillar_name"),
        item.get("hook_idea"),
        item.get("core_argument"),
        item.get("evidence_needed", ""),
        item.get("intended_response", ""),
        item.get("recommended_format", "problem_solution"),
        item.get("commercial_intent", ""),
        item.get("product_key"),
        item.get("status", "scheduled"),
        item.get("draft_id")
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": new_id, **item}

def update_calendar_item(item_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    set_clauses = []
    values = []
    for k, v in updates.items():
        if v is not None:
            set_clauses.append(f"{k} = ?")
            values.append(v)
    if set_clauses:
        values.append(item_id)
        conn.execute(f"UPDATE content_calendar SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
        conn.commit()
    row = conn.execute("SELECT * FROM content_calendar WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def clear_calendar_items() -> bool:
    conn = get_connection()
    conn.execute("DELETE FROM content_calendar")
    conn.commit()
    conn.close()
    return True

# 6. Post Drafts CRUD
def create_post_draft(draft_record: Dict[str, Any]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO post_drafts (
        idea_prompt, product_key, target_audience, content_pillar, voice_match_level,
        active_draft_format, concise_draft, story_draft, problem_solution_draft,
        technical_breakdown_draft, demo_draft, commercial_draft, metadata_json,
        final_edited_content, buyer_score_total, buyer_score_breakdown,
        claims_flagged, visual_suggestion, feedback_tag, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        draft_record.get("idea_prompt"),
        draft_record.get("product_key"),
        draft_record.get("target_audience"),
        draft_record.get("content_pillar"),
        draft_record.get("voice_match_level", 0.85),
        draft_record.get("active_draft_format", "problem_solution"),
        draft_record.get("concise_draft"),
        draft_record.get("story_draft"),
        draft_record.get("problem_solution_draft"),
        draft_record.get("technical_breakdown_draft"),
        draft_record.get("demo_draft"),
        draft_record.get("commercial_draft"),
        json.dumps(draft_record.get("metadata_json", {})),
        draft_record.get("final_edited_content"),
        draft_record.get("buyer_score_total"),
        json.dumps(draft_record.get("buyer_score_breakdown", {})),
        json.dumps(draft_record.get("claims_flagged", [])),
        draft_record.get("visual_suggestion"),
        draft_record.get("feedback_tag"),
        draft_record.get("status", "draft")
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_post_drafts(status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    if status:
        rows = conn.execute("SELECT * FROM post_drafts WHERE status = ? ORDER BY id DESC", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM post_drafts ORDER BY id DESC").fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        d["buyer_score_breakdown"] = json.loads(d["buyer_score_breakdown"]) if d.get("buyer_score_breakdown") else {}
        d["claims_flagged"] = json.loads(d["claims_flagged"]) if d.get("claims_flagged") else []
        d["metadata_json"] = json.loads(d["metadata_json"]) if d.get("metadata_json") else {}
        results.append(d)
    return results

def get_post_draft_by_id(draft_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM post_drafts WHERE id = ?", (draft_id,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["buyer_score_breakdown"] = json.loads(d["buyer_score_breakdown"]) if d.get("buyer_score_breakdown") else {}
    d["claims_flagged"] = json.loads(d["claims_flagged"]) if d.get("claims_flagged") else []
    d["metadata_json"] = json.loads(d["metadata_json"]) if d.get("metadata_json") else {}
    return d

def update_post_draft(draft_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    set_clauses = []
    values = []
    for k, v in updates.items():
        if v is not None:
            if k in ("buyer_score_breakdown", "claims_flagged", "metadata_json"):
                set_clauses.append(f"{k} = ?")
                values.append(json.dumps(v))
            else:
                set_clauses.append(f"{k} = ?")
                values.append(v)
    if set_clauses:
        values.append(draft_id)
        conn.execute(f"UPDATE post_drafts SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
        conn.commit()
    conn.close()
    return get_post_draft_by_id(draft_id)

# 7. Research Items CRUD
def get_research_items() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM research_items ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_research_item(item: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO research_items (
        title, source_url, source_type, raw_excerpt, analyst_notes,
        synthesized_problems, buyer_questions, industry_vocabulary, tags
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item.get("title"),
        item.get("source_url", ""),
        item.get("source_type", "article"),
        item.get("raw_excerpt", ""),
        item.get("analyst_notes", ""),
        item.get("synthesized_problems", ""),
        item.get("buyer_questions", ""),
        item.get("industry_vocabulary", ""),
        item.get("tags", "")
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": new_id, **item}

# 8. Post Performance CRUD
def log_post_performance(record: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO post_performance (
        post_draft_id, post_title, published_date, period_type,
        impressions, reactions, comments, reposts, profile_visits,
        connection_requests, inbound_dms, qualified_leads, sales_opportunities,
        revenue_attributed, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record.get("post_draft_id"),
        record.get("post_title", "Untitled Post"),
        record.get("published_date"),
        record.get("period_type", "24h"),
        record.get("impressions", 0),
        record.get("reactions", 0),
        record.get("comments", 0),
        record.get("reposts", 0),
        record.get("profile_visits", 0),
        record.get("connection_requests", 0),
        record.get("inbound_dms", 0),
        record.get("qualified_leads", 0),
        record.get("sales_opportunities", 0),
        record.get("revenue_attributed", 0.0),
        record.get("notes", "")
    ))
    new_id = cursor.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM post_performance WHERE id = ?", (new_id,)).fetchone()
    conn.close()
    return dict(row) if row else {"id": new_id, **record}

def get_performance_logs() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM post_performance ORDER BY published_date DESC, id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# 9. API Usage Log
def record_api_usage(endpoint: str, model: str, prompt_tokens: int, completion_tokens: int, estimated_cost_usd: float):
    conn = get_connection()
    conn.execute("""
    INSERT INTO api_usage_logs (endpoint, model, prompt_tokens, completion_tokens, total_tokens, estimated_cost_usd)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        endpoint,
        model,
        prompt_tokens,
        completion_tokens,
        prompt_tokens + completion_tokens,
        estimated_cost_usd
    ))
    conn.commit()
    conn.close()

def get_api_usage_summary() -> Dict[str, Any]:
    conn = get_connection()
    row = conn.execute("""
    SELECT 
        COUNT(*) as total_calls,
        COALESCE(SUM(prompt_tokens), 0) as total_prompt_tokens,
        COALESCE(SUM(completion_tokens), 0) as total_completion_tokens,
        COALESCE(SUM(total_tokens), 0) as total_tokens,
        COALESCE(SUM(estimated_cost_usd), 0.0) as total_cost_usd
    FROM api_usage_logs
    """).fetchone()
    conn.close()
    return dict(row) if row else {
        "total_calls": 0, "total_prompt_tokens": 0, "total_completion_tokens": 0, "total_tokens": 0, "total_cost_usd": 0.0
    }

# 10. Prospect Leads CRUD
def get_prospect_leads() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM prospect_leads ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_prospect_lead(lead: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO prospect_leads (
        prospect_name, company, role_title, website_url, origin_post_id,
        stage, deal_value_usd, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lead.get("prospect_name"),
        lead.get("company", ""),
        lead.get("role_title", ""),
        lead.get("website_url", ""),
        lead.get("origin_post_id"),
        lead.get("stage", "inbound_dm"),
        lead.get("deal_value_usd", 0.0),
        lead.get("notes", "")
    ))
    new_id = cursor.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM prospect_leads WHERE id = ?", (new_id,)).fetchone()
    conn.close()
    return dict(row) if row else {"id": new_id, **lead}

def update_prospect_lead(lead_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    set_clauses = []
    values = []
    for k, v in updates.items():
        if v is not None:
            set_clauses.append(f"{k} = ?")
            values.append(v)
    if set_clauses:
        values.append(lead_id)
        conn.execute(f"UPDATE prospect_leads SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
        conn.commit()
    row = conn.execute("SELECT * FROM prospect_leads WHERE id = ?", (lead_id,)).fetchone()
    conn.close()
    return dict(row) if row else None
