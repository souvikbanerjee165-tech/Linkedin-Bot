import json
import logging
from typing import Dict, Any, List
from app.services.deepseek_client import deepseek_client

logger = logging.getLogger("feed_radar")

class FeedConversationRadar:
    """
    LinkedIn Feed & Discussion Radar
    Inspired by PacemakerX/LinkedIntel.
    Given trending industry topics, competitor posts, or viral discussions:
    1. Analyzes buyer sentiment and underlying commercial objections.
    2. Crafts high-authority, value-additive comments (NOT generic engagement bait).
    3. Bridges the conversation organically to your software builder positioning (PodLeads AI / Dental Intel).
    """

    async def analyze_and_draft_response(
        self,
        post_content: str,
        poster_role: str = "B2B Decision Maker",
        target_product: str = "podleads_ai"
    ) -> Dict[str, Any]:
        sys_prompt = (
            "You are a B2B LinkedIn Engagement & Social Selling Strategist.\n"
            "Analyze a post from a prospect or industry leader. Draft 3 distinct comment responses that establish technical authority and spark natural inbound profile visits.\n"
            "Strict Guidelines:\n"
            "- NEVER say 'Great post!', 'Love this insight', or use fake hype.\n"
            "- Option 1 (Contrarian / Builder Reality): Adds an unmentioned trade-off or implementation obstacle.\n"
            "- Option 2 (Technical Clarification): Distinguishes deterministic business logic from LLM hype.\n"
            "- Option 3 (Conversation Hook): Asks a highly specific operational question that founders love answering.\n"
            "- Return a JSON object with: 'core_thesis', 'target_vulnerability', and 'comments' (list of 3 objects with 'style' and 'text')."
        )

        usr_prompt = (
            f"Poster Profile/Role: {poster_role}\n"
            f"Our Core Competency: AI automation, workflow systems builder (Product: {target_product})\n"
            f"Target Post Content:\n\"{post_content}\"\n\n"
            "Generate structured analysis and 3 high-authority comment drafts in JSON."
        )

        res = await deepseek_client.call_completion(
            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": usr_prompt}],
            temperature=0.6,
            response_format={"type": "json_object"},
            endpoint_name="feed_conversation_radar"
        )

        try:
            content_str = res["content"].strip()
            if "```json" in content_str:
                content_str = content_str.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(content_str)
            return parsed
        except Exception as exc:
            logger.warning(f"Radar JSON parse error: {exc}")
            return {
                "core_thesis": "Operational discussion around B2B workflows",
                "target_vulnerability": "Over-reliance on manual sorting before qualification",
                "comments": [
                    {"style": "Builder Reality", "text": "The bottleneck usually isn't generating more messages—it's verifying if the account actually has the problem before reaching out. Observable signals save 80% of sales reps' wasted time."},
                    {"style": "Technical Clarification", "text": "Deterministic data filters first, language models for synthesis second. When people invert that order, prompt drift ruins qualification."},
                    {"style": "Tactical Question", "text": "Curious how your team handles triage outside business hours? That's where we typically see the sharpest drop-off in practice workflows."}
                ]
            }

feed_radar = FeedConversationRadar()
