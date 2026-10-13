import pytest
from app.services.scoring_engine import scoring_engine

def test_buyer_intent_scoring_rubric():
    high_intent_post = """
Before buying an outreach tool for your sales team, check your observable digital signals first.

When we inspect dental clinics, 80% of manual friction comes from three things:
- Missing online booking capabilities causing patient drop-off
- Disconnected follow-up steps with zero lead prioritization
- Spending 15 hours weekly verifying information that could be checked programmatically

Fixing the workflow sequence first cuts operational drag before touching a single prompt.

Direct message me 'AUDIT' to see how we map workflow bottlenecks for your team.
"""
    result = scoring_engine.evaluate_draft(high_intent_post, target_audience="Agency Founders", product_key="podleads_ai")
    assert 0 <= result.total_score <= 100
    assert result.audience_relevance >= 14
    assert result.problem_specificity >= 14
    assert result.commercial_relevance >= 8
    assert result.cta_quality >= 4
    assert len(result.actionable_improvements) > 0

def test_slop_penalty_detection():
    slop_post = """
AI is transforming everything in today's fast-paced world! Unleash 10x your business with this revolutionary secret hack.
Agree? Thoughts?
"""
    result = scoring_engine.evaluate_draft(slop_post)
    # Penalized for buzzwords and engagement bait
    assert result.originality_usefulness <= 10
    assert any("buzzwords" in imp.lower() for imp in result.actionable_improvements)
