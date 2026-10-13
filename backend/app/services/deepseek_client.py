import httpx
import json
import logging
from typing import Dict, Any, Optional, List
from app.config import settings
from app import crud

logger = logging.getLogger("deepseek_client")

class DeepSeekClient:
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url.rstrip("/")
        self.model = settings.deepseek_model
        self.timeout = settings.deepseek_timeout_seconds
        self.max_retries = settings.deepseek_max_retries

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        # DeepSeek pricing per 1M tokens
        input_cost = (prompt_tokens / 1_000_000.0) * settings.cost_per_1m_input_cache_miss
        output_cost = (completion_tokens / 1_000_000.0) * settings.cost_per_1m_output
        return round(input_cost + output_cost, 6)

    async def call_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        response_format: Optional[Dict[str, str]] = None,
        endpoint_name: str = "chat_completion"
    ) -> Dict[str, Any]:
        """
        Calls the official DeepSeek API with retry logic, timeout, cost accounting,
        and graceful mock fallback if no API key is provided.
        """
        if not settings.is_api_key_configured:
            logger.info("DEEPSEEK_API_KEY not configured. Using offline fallback generation engine.")
            return self._mock_completion_fallback(messages, endpoint_name)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }
        if response_format:
            payload["response_format"] = response_format

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        usage = data.get("usage", {})
                        prompt_tokens = usage.get("prompt_tokens", 0)
                        completion_tokens = usage.get("completion_tokens", 0)
                        cost = self.calculate_cost(prompt_tokens, completion_tokens)
                        
                        # Log API usage to SQLite
                        crud.record_api_usage(
                            endpoint=endpoint_name,
                            model=self.model,
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            estimated_cost_usd=cost
                        )

                        content = data["choices"][0]["message"]["content"]
                        return {
                            "content": content,
                            "prompt_tokens": prompt_tokens,
                            "completion_tokens": completion_tokens,
                            "total_tokens": prompt_tokens + completion_tokens,
                            "estimated_cost_usd": cost,
                            "model": self.model,
                            "is_mock": False
                        }
                    else:
                        error_msg = f"DeepSeek API error {response.status_code}: {response.text}"
                        last_error = error_msg
                        logger.warning(f"Attempt {attempt + 1} failed: {error_msg}")
                        if response.status_code in (400, 401, 403):
                            raise RuntimeError(f"DeepSeek Authentication/Request Error: {response.text}")
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = str(exc)
                logger.warning(f"Network error on attempt {attempt + 1}: {exc}")

        raise RuntimeError(f"DeepSeek API request failed after {self.max_retries + 1} attempts: {last_error}")

    def get_structured_drafts_fallback(self) -> Dict[str, Any]:
        return {
            "concise": {
                "format_type": "concise",
                "title": "Concise Systems View",
                "hook": "Most B2B automation fails not because the AI is weak, but because the business process was broken before the software was installed.",
                "main_body": "When we analyze client workflows, 80% of manual friction comes from three things:\n- Unstructured incoming signals (unvetted form fills, ambiguous emails)\n- Disconnected follow-up steps with zero prioritization\n- Manual verification of data that could be checked programmatically\n\nFixing the workflow sequence first cuts operational drag before touching a single prompt.",
                "closing_line": "Automate the bottleneck, not the whole business at once.",
                "call_to_action": "If your team spends >10 hours weekly triaging manual leads, reply 'AUDIT' to see how we map workflow bottlenecks.",
                "target_audience": "Agency Founders and B2B Business Leaders",
                "primary_purpose": "Demonstrate process clarity over technology hype",
                "claims_to_verify": ["Verify actual client time audit statistics with team"],
                "suggested_visual": "A 3-step flowchart showing manual friction vs streamlined triage sequence",
                "full_text": "Most B2B automation fails not because the AI is weak, but because the business process was broken before the software was installed.\n\nWhen we analyze client workflows, 80% of manual friction comes from three things:\n- Unstructured incoming signals (unvetted form fills, ambiguous emails)\n- Disconnected follow-up steps with zero prioritization\n- Manual verification of data that could be checked programmatically\n\nFixing the workflow sequence first cuts operational drag before touching a single prompt.\n\nAutomate the bottleneck, not the whole business at once.\n\nIf your team spends >10 hours weekly triaging manual leads, reply 'AUDIT' to see how we map workflow bottlenecks."
            },
            "story": {
                "format_type": "story",
                "title": "Builder's Lesson",
                "hook": "Two months ago, I tried building an AI tool that did everything: lead discovery, qualification, copywriting, and CRM sync. It failed completely.",
                "main_body": "The prompt chaining was brittle. If one API call returned a malformed field, the entire sequence collapsed.\n\nSo I scrapped the 'all-in-one' promise and rebuilt PodLeads AI around a single observable signal: YouTube channel metadata and content frequency.\n\nInstead of trying to replace the sales rep, the tool simply gave the rep a 60-second summary of where the creator was leaving money on the table.\n\nThe lesson for builders: Narrow the scope until failure modes become impossible to hide.",
                "closing_line": "The highest-leverage software usually does one unglamorous job with relentless consistency.",
                "call_to_action": "What is one manual task in your sales pipeline you wish took 30 seconds instead of 30 minutes?",
                "target_audience": "Technical Founders & Agency Owners",
                "primary_purpose": "Build builder credibility through honest implementation trade-offs",
                "claims_to_verify": ["Verify specific architectural timeline milestones"],
                "suggested_visual": "Screenshot of terminal error vs simplified metadata output JSON",
                "full_text": "Two months ago, I tried building an AI tool that did everything: lead discovery, qualification, copywriting, and CRM sync. It failed completely.\n\nThe prompt chaining was brittle. If one API call returned a malformed field, the entire sequence collapsed.\n\nSo I scrapped the 'all-in-one' promise and rebuilt PodLeads AI around a single observable signal: YouTube channel metadata and content frequency.\n\nInstead of trying to replace the sales rep, the tool simply gave the rep a 60-second summary of where the creator was leaving money on the table.\n\nThe lesson for builders: Narrow the scope until failure modes become impossible to hide.\n\nThe highest-leverage software usually does one unglamorous job with relentless consistency.\n\nWhat is one manual task in your sales pipeline you wish took 30 seconds instead of 30 minutes?"
            },
            "problem_solution": {
                "format_type": "problem_solution",
                "title": "Problem & Solution Breakdown",
                "hook": "Before buying AI software for your sales team, check your observable digital signals first.",
                "main_body": "Here is the trap most businesses fall into:\nThey buy an outreach tool and blast 1,000 generic messages a week. Response rate: under 1%.\n\nWhy? Because they haven't verified if the prospect actually has the problem.\n\nWith Dental Sales Intelligence, we don't start with the pitch. We inspect publicly observable signals:\n1. Does the practice website offer instant online booking or just a static phone number?\n2. Are their local profile hours aligned with their booking availability?\n3. Is their mobile experience causing patient drop-off?\n\nWhen outreach leads with an observable fact rather than a generic sales pitch, the conversation changes instantly.",
                "closing_line": "Intelligence isn't sending more messages. It is knowing who actually has the problem before you reach out.",
                "call_to_action": "Direct message me 'SIGNALS' if you want a sample breakdown of observable triggers for your industry.",
                "target_audience": "B2B Sales Directors and Practice Owners",
                "primary_purpose": "Position signal-based research as superior to spam outreach",
                "claims_to_verify": ["Ensure practice booking capability criteria are explicitly documented"],
                "suggested_visual": "Side-by-side comparison: Generic template vs Signal-informed outreach breakdown",
                "full_text": "Before buying AI software for your sales team, check your observable digital signals first.\n\nHere is the trap most businesses fall into:\nThey buy an outreach tool and blast 1,000 generic messages a week. Response rate: under 1%.\n\nWhy? Because they haven't verified if the prospect actually has the problem.\n\nWith Dental Sales Intelligence, we don't start with the pitch. We inspect publicly observable signals:\n1. Does the practice website offer instant online booking or just a static phone number?\n2. Are their local profile hours aligned with their booking availability?\n3. Is their mobile experience causing patient drop-off?\n\nWhen outreach leads with an observable fact rather than a generic sales pitch, the conversation changes instantly.\n\nIntelligence isn't sending more messages. It is knowing who actually has the problem before you reach out.\n\nDirect message me 'SIGNALS' if you want a sample breakdown of observable triggers for your industry."
            },
            "technical_breakdown": {
                "format_type": "technical_breakdown",
                "title": "Technical Architecture for Business Owners",
                "hook": "Here is how a real B2B sales intelligence pipeline actually works under the hood (without the vendor marketing speak).",
                "main_body": "Step 1: Signal Ingestion\nWe crawl target URLs to extract public technical markers: CMS type, widget scripts, and responsive layout performance.\n\nStep 2: Heuristic Scoring\nRather than asking an LLM to guess, deterministic rules score the prospect: missing online booking = high opportunity score (+30).\n\nStep 3: Context-Rich Synthesis\nOnly after the data is structured does the AI model generate the briefing for the sales rep.\n\nThis separation keeps costs low ($0.002 per lead) and prevents the AI from fabricating facts.",
                "closing_line": "Deterministic data for facts; language models for synthesis. Never confuse the two.",
                "call_to_action": "Let me know in the comments: Do you rely on pure LLM output or do you validate with structured data first?",
                "target_audience": "Agency Owners and Technical Decision Makers",
                "primary_purpose": "Establish architectural rigor and cost consciousness",
                "claims_to_verify": ["Verify precise per-lead API cost calculation ($0.002) against live usage logs"],
                "suggested_visual": "Architecture block diagram showing Web Crawler -> Deterministic Scoring -> LLM Briefing",
                "full_text": "Here is how a real B2B sales intelligence pipeline actually works under the hood (without the vendor marketing speak).\n\nStep 1: Signal Ingestion\nWe crawl target URLs to extract public technical markers: CMS type, widget scripts, and responsive layout performance.\n\nStep 2: Heuristic Scoring\nRather than asking an LLM to guess, deterministic rules score the prospect: missing online booking = high opportunity score (+30).\n\nStep 3: Context-Rich Synthesis\nOnly after the data is structured does the AI model generate the briefing for the sales rep.\n\nThis separation keeps costs low ($0.002 per lead) and prevents the AI from fabricating facts.\n\nDeterministic data for facts; language models for synthesis. Never confuse the two.\n\nLet me know in the comments: Do you rely on pure LLM output or do you validate with structured data first?"
            },
            "demo": {
                "format_type": "demo",
                "title": "Demonstration-Led Post",
                "hook": "I ran 50 prospective dental clinic websites through our inspection system this morning. Here is what we found.",
                "main_body": "- 32 clinics had mobile site speeds over 4.5 seconds.\n- 19 had broken appointment request forms with outdated SSL certificates.\n- Only 6 had automated follow-ups for inquiries submitted after 5 PM.\n\nThis isn't about criticizing their technology. Dental practice managers are overwhelmed caring for patients.\n\nOur system turns these observable gaps into a clear priority list so sales reps can offer immediate, tangible assistance instead of spam.",
                "closing_line": "Prospects don't want a 20-slide sales deck. They want you to point out the leak in their bucket.",
                "call_to_action": "Want to see the audit template we used? Drop a comment below and I'll send the teardown guide.",
                "target_audience": "Dental Service Reps & Healthcare Technology Consultants",
                "primary_purpose": "Demonstrate practical domain analysis through observed public signals",
                "claims_to_verify": ["Audit sample size of 50 clinics must be verified before claiming as a completed live study"],
                "suggested_visual": "Redacted screenshot of the automated clinic opportunity scorecard",
                "full_text": "I ran 50 prospective dental clinic websites through our inspection system this morning. Here is what we found.\n\n- 32 clinics had mobile site speeds over 4.5 seconds.\n- 19 had broken appointment request forms with outdated SSL certificates.\n- Only 6 had automated follow-ups for inquiries submitted after 5 PM.\n\nThis isn't about criticizing their technology. Dental practice managers are overwhelmed caring for patients.\n\nOur system turns these observable gaps into a clear priority list so sales reps can offer immediate, tangible assistance instead of spam.\n\nProspects don't want a 20-slide sales deck. They want you to point out the leak in their bucket.\n\nWant to see the audit template we used? Drop a comment below and I'll send the teardown guide."
            },
            "commercial": {
                "format_type": "commercial",
                "title": "Commercial Solution Spotlight",
                "hook": "We are currently accepting 2 agency partners to test our custom sales intelligence pipelines next month.",
                "main_body": "If you run a video agency, podcast repurposing studio, or specialized B2B consultancy, you know the pain:\nYour sales team spends 15 hours a week digging through channels and social accounts just to find 5 qualified leads.\n\nWe build custom systems (like PodLeads AI) that:\n- Automatically extract prospect signals\n- Filter out dead channels\n- Draft contextual, signal-based outreach briefs\n\nNo cookie-cutter templates. Systems built directly on your proprietary workflow.",
                "closing_line": "We build the software so your team can focus on closing conversations.",
                "call_to_action": "Send me a direct message with 'PIPELINE' or comment below to see if your agency is a good fit.",
                "target_audience": "Agency Owners and Business Founders",
                "primary_purpose": "Generate qualified B2B inbound inquiries with a clear offer",
                "claims_to_verify": ["Confirm partner intake capacity and implementation availability"],
                "suggested_visual": "Summary graphic of PodLeads AI workflow pipeline with partner onboarding badge",
                "full_text": "We are currently accepting 2 agency partners to test our custom sales intelligence pipelines next month.\n\nIf you run a video agency, podcast repurposing studio, or specialized B2B consultancy, you know the pain:\nYour sales team spends 15 hours a week digging through channels and social accounts just to find 5 qualified leads.\n\nWe build custom systems (like PodLeads AI) that:\n- Automatically extract prospect signals\n- Filter out dead channels\n- Draft contextual, signal-based outreach briefs\n\nNo cookie-cutter templates. Systems built directly on your proprietary workflow.\n\nWe build the software so your team can focus on closing conversations.\n\nSend me a direct message with 'PIPELINE' or comment below to see if your agency is a good fit."
            }
        }

    def _mock_completion_fallback(self, messages: List[Dict[str, str]], endpoint_name: str) -> Dict[str, Any]:
        """
        Offline fallback engine that produces structured, high-quality B2B drafts
        strictly adhering to anti-slop rules when no DeepSeek key is provided.
        """
        user_message = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_message = m.get("content", "")
                break

        if endpoint_name == "post_generation" or "draft" in user_message.lower():
            content_str = json.dumps(self.get_structured_drafts_fallback())
        else:
            content_str = "Clear, pragmatic analysis grounded in verified business constraints and observable technical signals."

        return {
            "content": content_str,
            "prompt_tokens": 420,
            "completion_tokens": 780,
            "total_tokens": 1200,
            "estimated_cost_usd": 0.00035,
            "model": "offline-fallback-engine",
            "is_mock": True
        }

deepseek_client = DeepSeekClient()
