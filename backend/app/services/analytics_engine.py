from typing import Dict, Any, List
from app import crud
from app.schemas import PerformanceAnalyticsSummary

class PerformanceAnalyticsEngine:
    def compute_summary(self) -> PerformanceAnalyticsSummary:
        logs = crud.get_performance_logs()
        drafts = {d["id"]: d for d in crud.get_post_drafts()}
        
        total_posts = len(logs)
        total_imp = sum(l.get("impressions", 0) for l in logs)
        total_react = sum(l.get("reactions", 0) for l in logs)
        total_comm = sum(l.get("comments", 0) for l in logs)
        total_dms = sum(l.get("inbound_dms", 0) for l in logs)
        total_leads = sum(l.get("qualified_leads", 0) for l in logs)
        total_opps = sum(l.get("sales_opportunities", 0) for l in logs)
        total_rev = sum(l.get("revenue_attributed", 0.0) for l in logs)

        lead_conversion_rate = round((total_leads / max(1, total_imp)) * 100, 3) if total_imp > 0 else 0.0
        opp_rate = round((total_opps / max(1, total_leads)) * 100, 1) if total_leads > 0 else 0.0

        # Format breakdown
        format_stats: Dict[str, Dict[str, Any]] = {}
        for l in logs:
            post_id = l.get("post_draft_id")
            draft = drafts.get(post_id)
            fmt = draft.get("active_draft_format", "problem_solution") if draft else "problem_solution"
            if fmt not in format_stats:
                format_stats[fmt] = {"format": fmt, "posts": 0, "impressions": 0, "qualified_leads": 0, "inbound_dms": 0}
            format_stats[fmt]["posts"] += 1
            format_stats[fmt]["impressions"] += l.get("impressions", 0)
            format_stats[fmt]["qualified_leads"] += l.get("qualified_leads", 0)
            format_stats[fmt]["inbound_dms"] += l.get("inbound_dms", 0)

        best_formats = sorted(format_stats.values(), key=lambda x: (x["qualified_leads"], x["inbound_dms"]), reverse=True)

        # Content Pillar breakdown
        pillar_stats: Dict[str, Dict[str, Any]] = {
            "Practical AI Automation": {"pillar": "Practical AI Automation", "leads": 0, "posts": 0},
            "Behind-the-scenes Software Building": {"pillar": "Behind-the-scenes Software Building", "leads": 0, "posts": 0},
            "Observable Signal Teardowns": {"pillar": "Observable Signal Teardowns", "leads": 0, "posts": 0},
            "Commercial Partner Intake": {"pillar": "Commercial Partner Intake", "leads": 0, "posts": 0}
        }
        for l in logs:
            post_id = l.get("post_draft_id")
            draft = drafts.get(post_id)
            pillar = draft.get("content_pillar", "Practical AI Automation") if draft else "Practical AI Automation"
            if pillar not in pillar_stats:
                pillar_stats[pillar] = {"pillar": str(pillar), "leads": 0, "posts": 0}
            pillar_stats[pillar]["posts"] += 1
            pillar_stats[pillar]["leads"] += l.get("qualified_leads", 0)

        best_pillars = sorted(pillar_stats.values(), key=lambda x: x["leads"], reverse=True)

        # Recommendations based on data
        experiments = [
            "Test replacing generic 'What do you think?' calls to action with specific signal audit offers (e.g. 'Reply SIGNALS for a teardown of your market').",
            "Contrast high-reach posts with high-conversion posts: Compare whether breakdown posts or demonstration posts yield higher qualified DMs per 1,000 impressions.",
            "Run a controlled test comparing short text hooks vs technical architecture diagrams for B2B agency founder decision makers."
        ]

        return PerformanceAnalyticsSummary(
            total_posts_tracked=total_posts,
            total_impressions=total_imp,
            total_reactions=total_react,
            total_comments=total_comm,
            total_inbound_dms=total_dms,
            total_qualified_leads=total_leads,
            total_sales_opportunities=total_opps,
            total_revenue_attributed=total_rev,
            lead_conversion_rate=lead_conversion_rate,
            opportunity_rate=opp_rate,
            best_performing_formats=best_formats,
            best_performing_pillars=best_pillars,
            recommended_experiments=experiments
        )

analytics_engine = PerformanceAnalyticsEngine()
