import json
import logging
from typing import Dict, Any, List, Optional
from app.services.deepseek_client import deepseek_client
from app import crud

logger = logging.getLogger("multi_agent_writer")

class MultiAgentWriterPipeline:
    """
    Multi-Agent Writing Architecture inspired by rk-vashista/writer and sujeetgund/linkedin-post-generator-agent.
    Divides content creation into 3 distinct specialized roles:
    1. Researcher Agent: Extracts the core friction point, observable signals, and technical mechanism.
    2. Hook Specialist: Generates 3 anti-slop, high-curiosity opening hooks with strict cutoff discipline.
    3. Executive Editor & Format Crafter: Assembles the 6 required draft formats, strips fluff, and flags unverified claims.
    """

    async def run_pipeline(
        self,
        idea_prompt: str,
        target_audience: str,
        product: Dict[str, Any],
        brand: Dict[str, Any],
        all_knowledge: List[Dict[str, Any]],
        content_pillar: str,
        voice_profile: Dict[str, Any],
        commercial_intent: str,
        additional_context: str = ""
    ) -> Dict[str, Any]:
        verified_facts = [
            f"- {k['title']}: {k['claim_content']}"
            for k in all_knowledge if k.get("category") == "verified_fact"
        ]
        unverified_hypotheses = [
            f"- {k['title']}: {k['claim_content']}"
            for k in all_knowledge if k.get("category") in ("unverified_hypothesis", "needs_approval")
        ]

        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_cost = 0.0

        # ==========================================
        # AGENT 1: Researcher & Mechanism Extractor
        # ==========================================
        agent1_system = (
            "You are the Lead Technical Researcher in a B2B LinkedIn publishing team.\n"
            "Your objective: Analyze the author's post idea and extract the concrete technical mechanism and observable business bottleneck.\n"
            "Strict constraints: Do NOT write marketing hype or high-level platitudes. Focus on what is broken, what data signal is observed, and why businesses waste hours.\n"
            "Return a JSON object with: 'core_bottleneck', 'observable_signal', 'tactical_takeaway'."
        )
        agent1_user = (
            f"Idea: \"{idea_prompt}\"\n"
            f"Product: {product.get('name')} (Verified: {', '.join(product.get('verified_capabilities', []))})\n"
            f"Audience: {target_audience}\n"
            f"Facts: {'; '.join(verified_facts[:4])}\n"
            f"Additional Context: {additional_context}\n"
            "Extract the concrete bottleneck and technical angle in JSON."
        )
        res1 = await deepseek_client.call_completion(
            messages=[{"role": "system", "content": agent1_system}, {"role": "user", "content": agent1_user}],
            temperature=0.4,
            response_format={"type": "json_object"},
            endpoint_name="agent_researcher"
        )
        total_prompt_tokens += res1.get("prompt_tokens", 0)
        total_completion_tokens += res1.get("completion_tokens", 0)
        total_cost += res1.get("estimated_cost_usd", 0.0)

        research_summary = {}
        try:
            c1 = res1["content"].strip()
            if "```json" in c1:
                c1 = c1.split("```json")[1].split("```")[0].strip()
            research_summary = json.loads(c1)
        except Exception:
            research_summary = {
                "core_bottleneck": idea_prompt,
                "observable_signal": "Manual triage friction",
                "tactical_takeaway": "Test signals before buying software."
            }

        # ==========================================
        # AGENT 2: Anti-Slop Hook Specialist
        # ==========================================
        agent2_system = (
            "You are an Elite LinkedIn Hook Strategist.\n"
            "Your mission: Craft 3 distinctive, high-stopping-power opening hooks for business owners and agency founders.\n"
            "Anti-Slop Directives:\n"
            "- NEVER use 'In today's fast-paced world', 'AI is revolutionizing', or 'Are you ready?'.\n"
            "- Every hook must be under 140 characters and force the reader to stop scrolling without cheap clickbait.\n"
            "- Return a JSON object with a key 'hooks' containing a list of 3 strings."
        )
        agent2_user = (
            f"Core Bottleneck: {research_summary.get('core_bottleneck')}\n"
            f"Observable Signal: {research_summary.get('observable_signal')}\n"
            f"Target Audience: {target_audience}\n"
            f"Pillar: {content_pillar}\n"
            "Draft 3 distinct hooks in JSON."
        )
        res2 = await deepseek_client.call_completion(
            messages=[{"role": "system", "content": agent2_system}, {"role": "user", "content": agent2_user}],
            temperature=0.7,
            response_format={"type": "json_object"},
            endpoint_name="agent_hook_specialist"
        )
        total_prompt_tokens += res2.get("prompt_tokens", 0)
        total_completion_tokens += res2.get("completion_tokens", 0)
        total_cost += res2.get("estimated_cost_usd", 0.0)

        hook_variations = []
        try:
            c2 = res2["content"].strip()
            if "```json" in c2:
                c2 = c2.split("```json")[1].split("```")[0].strip()
            parsed_hooks = json.loads(c2)
            if isinstance(parsed_hooks, dict) and "hooks" in parsed_hooks:
                hook_variations = parsed_hooks["hooks"]
        except Exception:
            hook_variations = [f"Before buying AI software for your sales team, check your observable digital signals first."]

        # ==========================================
        # AGENT 3: Executive Editor & Draft Crafter
        # ==========================================
        agent3_system = (
            "You are the Executive Managing Editor for a B2B Software Builder.\n"
            "Using the research and tested hooks provided, write the final 6 distinct LinkedIn post drafts:\n"
            "1. concise, 2. story, 3. problem_solution, 4. technical_breakdown, 5. demo, 6. commercial.\n\n"
            "Strict Constraints:\n"
            "- Never invent customer revenue, client names, or live case studies.\n"
            "- Never claim concept features as live in production.\n"
            "- Keep sentence structures varied and direct. No emojis walls. No engagement-bait.\n"
            "- Return a valid JSON object with key 'drafts' containing a list of all 6 formats or keyed by format."
        )
        agent3_user = (
            f"Idea: \"{idea_prompt}\"\n"
            f"Researcher Brief: {json.dumps(research_summary)}\n"
            f"Selected Best Hook: {hook_variations[0] if hook_variations else ''}\n"
            f"Product: {product.get('name')} (Verified: {', '.join(product.get('verified_capabilities', []))}; Concept: {', '.join(product.get('concept_capabilities', []))})\n"
            f"Audience: {target_audience} | Pillar: {content_pillar}\n"
            f"Voice Avg Words: ~{voice_profile.get('typical_sentence_length', 14)}\n"
            f"Verified Facts: {'; '.join(verified_facts[:4])}\n"
            f"Flagged Hypotheses (MUST NOT STATE AS FACT): {'; '.join(unverified_hypotheses[:3])}\n"
            "Generate the 6 full draft formats in JSON."
        )
        res3 = await deepseek_client.call_completion(
            messages=[{"role": "system", "content": agent3_system}, {"role": "user", "content": agent3_user}],
            temperature=0.7,
            response_format={"type": "json_object"},
            endpoint_name="agent_executive_editor"
        )
        total_prompt_tokens += res3.get("prompt_tokens", 0)
        total_completion_tokens += res3.get("completion_tokens", 0)
        total_cost += res3.get("estimated_cost_usd", 0.0)

        return {
            "content": res3["content"],
            "research_summary": research_summary,
            "hook_variations": hook_variations,
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "total_tokens": total_prompt_tokens + total_completion_tokens,
            "estimated_cost_usd": round(total_cost, 6),
            "model": res3.get("model", "deepseek-chat"),
            "is_mock": res3.get("is_mock", False)
        }

multi_agent_pipeline = MultiAgentWriterPipeline()
