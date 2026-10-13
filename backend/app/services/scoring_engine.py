import re
from typing import Dict, Any, List
from app.schemas import BuyerIntentScoringBreakdown

class BuyerIntentScoringEngine:
    def __init__(self):
        self.slop_triggers = [
            "ai is transforming everything",
            "game-changer",
            "revolutionary",
            "skyrocket",
            "secret hack",
            "10x your",
            "unleash",
            "in today's fast-paced world",
            "dive deep",
            "delve",
            "testament",
            "tapestry",
            "viral",
            "comment below to receive",
            "agree?",
            "thoughts?"
        ]
        
        self.buyer_keywords = [
            "pipeline", "workflow", "bottleneck", "roi", "lead", "revenue",
            "cost", "implementation", "agency", "friction", "margin", "retention",
            "signal", "conversion", "decision-maker", "operations", "triage", "rep"
        ]

    def evaluate_draft(self, draft_text: str, target_audience: str = "", product_key: str = "") -> BuyerIntentScoringBreakdown:
        text_lower = draft_text.lower()
        word_count = len(draft_text.split())
        lines = [line.strip() for line in draft_text.split("\n") if line.strip()]
        
        # 1. Audience Relevance (Max 20)
        audience_score = 14
        if any(w in text_lower for w in ["founder", "agency", "decision", "owner", "director", "sales rep", "manager", "team"]):
            audience_score += 4
        if len(target_audience) > 5 and any(term in text_lower for term in target_audience.lower().split()[:2]):
            audience_score += 2
        audience_score = min(20, max(5, audience_score))

        # 2. Problem Specificity (Max 20)
        problem_score = 12
        if any(w in text_lower for w in ["bottleneck", "friction", "hours", "manual", "drop-off", "error", "unvetted", "broken", "unresponsive"]):
            problem_score += 5
        if re.search(r"\d+\s*(%|hours|minutes|seconds|leads|clinics|days)", text_lower):
            problem_score += 3
        problem_score = min(20, max(6, problem_score))

        # 3. Evidence and Credibility (Max 20)
        evidence_score = 12
        if any(w in text_lower for w in ["we built", "tested", "analyzed", "crawled", "inspected", "found that", "under the hood", "step 1"]):
            evidence_score += 5
        if "i tried" in text_lower or "failed" in text_lower or "trade-off" in text_lower or "lesson" in text_lower:
            evidence_score += 3
        evidence_score = min(20, max(5, evidence_score))

        # 4. Originality and Usefulness (Max 15)
        originality_score = 11
        # Deduct if slop detected
        slop_detected = [s for s in self.slop_triggers if s in text_lower]
        if slop_detected:
            originality_score -= min(5, len(slop_detected) * 2)
        if any(w in text_lower for w in ["instead of", "not because", "rather than", "deterministic", "observable signal"]):
            originality_score += 4
        originality_score = min(15, max(4, originality_score))

        # 5. Readability (Max 10)
        readability_score = 8
        avg_line_len = sum(len(l.split()) for l in lines) / max(1, len(lines))
        if 8 <= avg_line_len <= 25 and 80 <= word_count <= 350:
            readability_score += 2
        elif word_count < 40 or word_count > 500:
            readability_score -= 2
        readability_score = min(10, max(3, readability_score))

        # 6. Commercial Relevance (Max 10)
        commercial_score = 6
        buyer_hits = sum(1 for k in self.buyer_keywords if k in text_lower)
        if buyer_hits >= 3:
            commercial_score += 3
        if any(w in text_lower for w in ["custom", "solution", "system", "consultancy", "audit", "partner"]):
            commercial_score += 1
        commercial_score = min(10, max(3, commercial_score))

        # 7. Call-to-Action Quality (Max 5)
        cta_score = 3
        has_natural_cta = any(w in text_lower for w in ["reply", "message me", "dm", "comment", "let me know", "drop a comment"])
        if has_natural_cta:
            cta_score += 2
        if any(w in text_lower for w in ["agree?", "thoughts?", "like and repost"]):
            cta_score -= 1  # Penalty for engagement-bait CTA
        cta_score = min(5, max(1, cta_score))

        total_score = (
            audience_score +
            problem_score +
            evidence_score +
            originality_score +
            readability_score +
            commercial_score +
            cta_score
        )

        # Build rationales & improvements
        scoring_rationale = {
            "audience_relevance": f"{audience_score}/20: Reader profile alignment evaluated against decision-maker role.",
            "problem_specificity": f"{problem_score}/20: Assessment of whether operational friction is concrete or vague.",
            "evidence_credibility": f"{evidence_score}/20: Practical proof points, architecture steps, or builder lessons observed.",
            "originality_usefulness": f"{originality_score}/15: Grounded angle check; penalized {len(slop_detected)} generic hype markers.",
            "readability": f"{readability_score}/10: Pacing, line lengths ({round(avg_line_len, 1)} words/line), and skimmability.",
            "commercial_relevance": f"{commercial_score}/10: Alignment with business services and lead generation without hard pitching.",
            "cta_quality": f"{cta_score}/5: Contextual invitation evaluated for natural conversation initiation."
        }

        actionable_improvements = []
        if audience_score < 16:
            actionable_improvements.append("Directly name the operational role (e.g., 'Agency founders managing 10+ active editing pipelines') in the opening two sentences.")
        if problem_score < 16:
            actionable_improvements.append("Replace generalized issues with an exact operational cost (e.g. '15 hours lost weekly to unvetted lead qualification').")
        if evidence_score < 16:
            actionable_improvements.append("Include a specific architectural step, observable signal metric, or explicit trade-off learned during building.")
        if slop_detected:
            actionable_improvements.append(f"Remove generic buzzwords: {', '.join(slop_detected)}.")
        if cta_score < 4:
            actionable_improvements.append("Replace vague engagement questions with a low-friction commercial offer (e.g. 'Message me AUDIT to see how we map workflow bottlenecks').")

        if not actionable_improvements:
            actionable_improvements.append("Draft is highly focused, grounded, and commercially aligned. Ready for final proofread.")

        return BuyerIntentScoringBreakdown(
            audience_relevance=audience_score,
            problem_specificity=problem_score,
            evidence_credibility=evidence_score,
            originality_usefulness=originality_score,
            readability=readability_score,
            commercial_relevance=commercial_score,
            cta_quality=cta_score,
            total_score=total_score,
            scoring_rationale=scoring_rationale,
            actionable_improvements=actionable_improvements
        )

scoring_engine = BuyerIntentScoringEngine()
