import asyncio
import ipaddress
import socket
import time
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Playwright, Browser
from app.config import settings


def validate_public_url(target_url: str) -> str:
    """
    Validates that target_url uses http/https and resolves strictly to public IP addresses.
    Raises ValueError if the URL targets localhost, loopback, link-local, or private subnets (SSRF defense).
    """
    raw = (target_url or "").strip()
    if not raw:
        raise ValueError("URL cannot be empty.")
    if not raw.startswith("http://") and not raw.startswith("https://"):
        if "://" in raw:
            raise ValueError("Only http:// and https:// URLs are allowed.")
        raw = "https://" + raw

    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http:// and https:// schemes are permitted.")

    hostname = (parsed.hostname or "").strip().lower()
    if not hostname:
        raise ValueError("Invalid URL hostname.")

    if hostname in ("localhost", "0.0.0.0") or hostname.endswith(".local") or hostname.endswith(".internal"):
        raise ValueError(f"Blocked internal/local hostname: {hostname}")

    # Check if hostname is a literal IP first
    try:
        ip_obj = ipaddress.ip_address(hostname)
        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_reserved
            or ip_obj.is_unspecified
        ):
            raise ValueError(f"Blocked non-public IP address: {hostname}")
        return raw
    except ValueError as exc:
        if "Blocked" in str(exc):
            raise

    # Resolve DNS and inspect all returned IP addresses
    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise ValueError(f"Unable to resolve hostname '{hostname}': {exc}")

    for entry in addr_info:
        ip_str = entry[4][0]
        ip_obj = ipaddress.ip_address(ip_str)
        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_reserved
            or ip_obj.is_unspecified
        ):
            raise ValueError(f"Blocked hostname '{hostname}' resolving to non-public IP {ip_str}")

    return raw


class WebSignalInspector:
    def __init__(self):
        self.screenshots_dir = Path(settings.uploads_dir) / "signals"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._lock = asyncio.Lock()

        # Booking engines and SaaS widgets commonly observed on dental/service sites
        self.booking_signatures = [
            "zocdoc", "nexhealth", "localmed", "curvehero", "dentrix",
            "opendental", "patientpop", "weave", "solutionreach", "acuityscheduling",
            "calendly", "hubspot", "appointlet", "setmore", "square.site"
        ]

        # Chat & AI front-desk widgets
        self.chat_widget_signatures = [
            "intercom", "drift", "tidio", "gohighlevel", "leadconnectorhq",
            "podium", "birdeye", "zendesk", "crisp.chat", "livechatinc", "tawk.to"
        ]

    async def _get_browser(self) -> Browser:
        async with self._lock:
            if self._browser is not None and self._browser.is_connected():
                return self._browser
            if self._playwright is None:
                self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)
            return self._browser

    async def close(self):
        async with self._lock:
            if self._browser is not None:
                try:
                    await self._browser.close()
                except Exception:
                    pass
                self._browser = None
            if self._playwright is not None:
                try:
                    await self._playwright.stop()
                except Exception:
                    pass
                self._playwright = None

    async def inspect_website(self, target_url: str) -> Dict[str, Any]:
        """
        Visits a public website or YouTube channel using a reusable Playwright Chromium instance
        after enforcing SSRF validation, extracting booking widgets, chat/front-desk tools,
        H1/meta tags, local map signals, or YouTube channel metadata for PodLeads AI.
        """
        target_url = validate_public_url(target_url)

        start_time = time.time()
        parsed = urlparse(target_url)
        hostname = (parsed.hostname or "site").replace(":", "_").replace(".", "_")
        screenshot_filename = f"audit_{hostname}_{int(time.time())}.png"
        screenshot_path = self.screenshots_dir / screenshot_filename

        is_youtube = "youtube.com" in hostname or "youtu.be" in hostname

        signals: Dict[str, Any] = {
            "target_url": target_url,
            "signal_mode": "youtube_channel" if is_youtube else "website_audit",
            "inspected_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "page_title": "",
            "h1_headline": "",
            "meta_description": "",
            "load_time_seconds": 0.0,
            "has_ssl": target_url.startswith("https://"),
            "has_interactive_booking": False,
            "detected_booking_vendors": [],
            "has_chat_widget": False,
            "detected_chat_widgets": [],
            "has_phone_callout": False,
            "has_contact_form": False,
            "has_google_maps_or_reviews": False,
            "youtube_signals": {},
            "screenshot_url": f"/uploads/signals/{screenshot_filename}",
            "opportunity_score": 0,
            "observable_bottlenecks": [],
            "outreach_angle": ""
        }

        browser = await self._get_browser()
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
            signals["load_time_seconds"] = round(time.time() - start_time, 2)
            signals["page_title"] = await page.title()

            # Extract H1 and meta description
            h1_el = await page.query_selector("h1")
            if h1_el:
                signals["h1_headline"] = (await h1_el.inner_text()).strip()[:160]

            meta_el = await page.query_selector("meta[name='description'], meta[property='og:description']")
            if meta_el:
                signals["meta_description"] = ((await meta_el.get_attribute("content")) or "").strip()[:240]

            # Take viewport screenshot
            await page.screenshot(path=str(screenshot_path), full_page=False)

            content = (await page.content()).lower()

            if is_youtube:
                # Extract PodLeads AI YouTube channel/video signals
                has_links_in_bio = "redirect" in content or "http" in signals["meta_description"].lower()
                signals["youtube_signals"] = {
                    "channel_or_video_title": signals["page_title"],
                    "description_snippet": signals["meta_description"],
                    "has_external_funnel_links": has_links_in_bio
                }
            else:
                # Detect booking vendors
                for vendor in self.booking_signatures:
                    if vendor in content:
                        signals["detected_booking_vendors"].append(vendor)
                signals["has_interactive_booking"] = len(signals["detected_booking_vendors"]) > 0

                # Detect chat / AI front-desk widgets
                for widget in self.chat_widget_signatures:
                    if widget in content:
                        signals["detected_chat_widgets"].append(widget)
                signals["has_chat_widget"] = len(signals["detected_chat_widgets"]) > 0

                # Detect phone number triggers
                if "tel:" in content or "call " in content or "phone" in content:
                    signals["has_phone_callout"] = True

                # Detect Google Maps / Local review embeds
                if "google.com/maps" in content or "maps.googleapis.com" in content or "google reviews" in content:
                    signals["has_google_maps_or_reviews"] = True

                # Detect contact/appointment forms
                forms = await page.query_selector_all("form")
                signals["has_contact_form"] = len(forms) > 0

        except Exception as exc:
            signals["observable_bottlenecks"].append(f"Connection issue or timeout: {str(exc)[:80]}")
        finally:
            await context.close()

        # Compute Opportunity Score (higher = more manual friction & opportunity for our systems)
        opp_score = 40
        bottlenecks: List[str] = list(signals["observable_bottlenecks"])

        if is_youtube:
            if not signals["youtube_signals"].get("has_external_funnel_links"):
                opp_score += 35
                bottlenecks.append("YouTube channel description lacks clear lead-capture or funnel attribution links.")
            else:
                opp_score += 20
                bottlenecks.append("Active creator funnel detected — candidate for short-form repurposing and automated sponsor/lead qualification.")
            signals["opportunity_score"] = min(100, opp_score)
            signals["observable_bottlenecks"] = bottlenecks
            signals["outreach_angle"] = (
                f"PodLeads AI Signal Audit for '{signals['page_title']}': Channel content can be systematically repurposed "
                "and paired with automated lead-capture links to convert viewers into booked calls."
            )
            return signals

        if not signals["has_interactive_booking"]:
            opp_score += 30
            bottlenecks.append("Missing instant online booking (relies exclusively on phone calls or static email forms).")
        else:
            bottlenecks.append(f"Detected 3rd-party booking widget: {', '.join(signals['detected_booking_vendors'])}.")

        if not signals["has_chat_widget"]:
            opp_score += 15
            bottlenecks.append("No interactive patient/lead chat or AI front-desk widget detected for after-hours inquiries.")
        else:
            bottlenecks.append(f"Detected chat/front-desk widget: {', '.join(signals['detected_chat_widgets'])}.")

        if signals["load_time_seconds"] > 3.5:
            opp_score += 10
            bottlenecks.append(f"Slow initial page response ({signals['load_time_seconds']}s load time).")

        if not signals["has_contact_form"] and not signals["has_interactive_booking"]:
            opp_score += 10
            bottlenecks.append("No observable digital lead capture mechanism found on homepage.")

        if not signals["has_google_maps_or_reviews"]:
            opp_score += 5
            bottlenecks.append("No embedded Google Maps or local review proof detected on landing page.")

        signals["opportunity_score"] = min(100, opp_score)
        signals["observable_bottlenecks"] = bottlenecks

        if not signals["has_interactive_booking"] and not signals["has_chat_widget"]:
            signals["outreach_angle"] = (
                "Practice relies strictly on manual phone triage with zero online booking or after-hours chat capture. "
                "Prospective patients browsing after 5 PM face immediate drop-off."
            )
        elif signals["has_interactive_booking"] and not signals["has_chat_widget"]:
            signals["outreach_angle"] = (
                f"Practice uses {signals['detected_booking_vendors'][0]} for scheduling, but lacks automated inquiry/missed-call triage for patients with questions before booking."
            )
        else:
            signals["outreach_angle"] = (
                "Practice has baseline digital widgets installed; opportunity lies in unifying lead qualification and recall follow-ups."
            )

        return signals

signal_inspector = WebSignalInspector()
