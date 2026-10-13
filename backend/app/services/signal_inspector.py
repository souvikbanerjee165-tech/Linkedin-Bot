import asyncio
import time
import os
from pathlib import Path
from typing import Dict, Any, List
from playwright.async_api import async_playwright
from app.config import settings

class WebSignalInspector:
    def __init__(self):
        self.screenshots_dir = Path(settings.uploads_dir) / "signals"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Booking engines and SaaS widgets commonly observed on dental/service sites
        self.booking_signatures = [
            "zocdoc", "nexhealth", "localmed", "curvehero", "dentrix",
            "opendental", "patientpop", "weave", "solutionreach", "acuityscheduling",
            "calendly", "hubspot", "appointlet", "setmore", "square.site"
        ]

    async def inspect_website(self, target_url: str) -> Dict[str, Any]:
        """
        Visits a public website using Playwright Chromium to inspect observable digital signals,
        detect online booking infrastructure, take a high-res screenshot, and compute an opportunity score.
        """
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = "https://" + target_url

        start_time = time.time()
        hostname = target_url.split("//")[-1].split("/")[0].replace(":", "_").replace(".", "_")
        screenshot_filename = f"audit_{hostname}_{int(time.time())}.png"
        screenshot_path = self.screenshots_dir / screenshot_filename

        signals = {
            "target_url": target_url,
            "inspected_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "page_title": "",
            "load_time_seconds": 0.0,
            "has_ssl": target_url.startswith("https://"),
            "has_interactive_booking": False,
            "detected_booking_vendors": [],
            "has_phone_callout": False,
            "has_contact_form": False,
            "screenshot_url": f"/uploads/signals/{screenshot_filename}",
            "opportunity_score": 0,
            "observable_bottlenecks": [],
            "outreach_angle": ""
        }

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                response = await page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
                signals["load_time_seconds"] = round(time.time() - start_time, 2)
                signals["page_title"] = await page.title()

                # Take viewport screenshot
                await page.screenshot(path=str(screenshot_path), full_page=False)

                # Inspect page content and script tags
                content = (await page.content()).lower()

                # Detect booking vendors
                for vendor in self.booking_signatures:
                    if vendor in content:
                        signals["detected_booking_vendors"].append(vendor)

                signals["has_interactive_booking"] = len(signals["detected_booking_vendors"]) > 0

                # Detect phone number triggers
                if "tel:" in content or "call " in content or "phone" in content:
                    signals["has_phone_callout"] = True

                # Detect contact/appointment forms
                forms = await page.query_selector_all("form")
                signals["has_contact_form"] = len(forms) > 0

            except Exception as exc:
                signals["observable_bottlenecks"].append(f"Connection issue or timeout: {str(exc)[:80]}")
            finally:
                await browser.close()

        # Compute Opportunity Score (higher = more manual friction & opportunity for our systems)
        opp_score = 40  # base
        bottlenecks = []

        if not signals["has_interactive_booking"]:
            opp_score += 35
            bottlenecks.append("Missing instant online booking (relies exclusively on phone calls or static email forms).")
        else:
            bottlenecks.append(f"Detected 3rd-party widget: {', '.join(signals['detected_booking_vendors'])}.")

        if signals["load_time_seconds"] > 3.5:
            opp_score += 15
            bottlenecks.append(f"Slow initial page response ({signals['load_time_seconds']}s load time).")

        if not signals["has_contact_form"] and not signals["has_interactive_booking"]:
            opp_score += 10
            bottlenecks.append("No observable digital lead capture mechanism found on homepage.")

        signals["opportunity_score"] = min(100, opp_score)
        signals["observable_bottlenecks"] = bottlenecks

        # Outreach / Post Hook angle
        if not signals["has_interactive_booking"]:
            signals["outreach_angle"] = f"Practice relies strictly on manual phone triage. Patients looking to book outside 9-5 clinic hours face complete drop-off."
        else:
            signals["outreach_angle"] = f"Practice has online booking installed via {signals['detected_booking_vendors'][0] if signals['detected_booking_vendors'] else 'widget'}, but lacks automated missed-call triage."

        return signals

signal_inspector = WebSignalInspector()
