import re
from typing import Dict, Any, List
from app import crud

class WritingVoiceEngine:
    def analyze_writing_samples(self, samples: List[str]) -> Dict[str, Any]:
        if not samples:
            return crud.get_voice_profile()

        combined_text = " ".join(samples)
        sentences = [s.strip() for s in re.split(r"[.!?]+", combined_text) if len(s.strip()) > 3]
        words = combined_text.split()
        
        if not sentences:
            avg_sentence_len = 14.5
        else:
            avg_sentence_len = round(len(words) / max(1, len(sentences)), 1)

        # Heuristic tone detection
        text_lower = combined_text.lower()
        formal_markers = ["furthermore", "consequently", "specifically", "methodology", "infrastructure", "subsequently"]
        tech_markers = ["api", "pipeline", "schema", "architecture", "crawler", "json", "python", "fastapi", "endpoint", "database"]
        direct_markers = ["i built", "i noticed", "here is why", "do not", "never", "stop", "lesson", "trade-off"]
        humor_markers = ["ironically", "funny thing", "spoiler", "of course", "surprise"]

        formality = min(1.0, max(0.1, sum(1 for m in formal_markers if m in text_lower) / 10.0 + 0.35))
        technical = min(1.0, max(0.2, sum(1 for m in tech_markers if m in text_lower) / 8.0 + 0.40))
        directness = min(1.0, max(0.3, sum(1 for m in direct_markers if m in text_lower) / 6.0 + 0.50))
        humor = min(1.0, max(0.05, sum(1 for m in humor_markers if m in text_lower) / 5.0 + 0.15))

        profile_updates = {
            "typical_sentence_length": avg_sentence_len,
            "formality_level": round(formality, 2),
            "technical_depth": round(technical, 2),
            "directness_confidence": round(directness, 2),
            "humor_level": round(humor, 2),
            "storytelling_style": "Direct builder experience: states real operational problems, explains systems built, shares honest friction points, and summarizes tangible outcomes.",
            "vocabulary_phrasing": "Pragmatic, system-oriented, transparent. Emphasizes workflows, observable signals, and friction points. Never relies on buzzwords.",
            "stylistic_habits": f"Presents ideas in short, skimmable paragraphs with average sentence length of ~{avg_sentence_len} words."
        }

        crud.update_voice_profile(profile_updates)
        return crud.get_voice_profile()

    def record_feedback(self, draft_id: int, feedback_tag: str) -> Dict[str, Any]:
        """
        Feedback tags:
        'Sounds like me', 'Too formal', 'Too promotional', 'Too generic', 'Too artificial', 'Too technical', 'Good to publish'
        """
        current_profile = crud.get_voice_profile()
        feedback_history = current_profile.get("feedback_history") or ""
        updated_history = (feedback_history + f"\n[Draft #{draft_id}]: {feedback_tag}").strip()
        
        # Adaptive tuning based on feedback
        updates: Dict[str, Any] = {"feedback_history": updated_history}
        if feedback_tag == "Too formal":
            updates["formality_level"] = max(0.2, current_profile.get("formality_level", 0.5) - 0.1)
        elif feedback_tag == "Too promotional":
            updates["directness_confidence"] = max(0.4, current_profile.get("directness_confidence", 0.8) - 0.05)
        elif feedback_tag == "Too generic":
            updates["technical_depth"] = min(0.9, current_profile.get("technical_depth", 0.6) + 0.1)
        elif feedback_tag == "Too technical":
            updates["technical_depth"] = max(0.3, current_profile.get("technical_depth", 0.6) - 0.1)
        elif feedback_tag == "Sounds like me" or feedback_tag == "Good to publish":
            # reinforce current levels
            updates["voice_match_default"] = min(0.95, current_profile.get("voice_match_default", 0.8) + 0.02)

        crud.update_voice_profile(updates)
        crud.update_post_draft(draft_id, {"feedback_tag": feedback_tag})
        return crud.get_voice_profile()

voice_engine = WritingVoiceEngine()
