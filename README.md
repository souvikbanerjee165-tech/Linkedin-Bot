# LinkedIn B2B Growth & Sales Copilot

A local-first web application designed for a technical software builder, automation specialist, and digital marketer to grow a personal LinkedIn presence and generate qualified B2B leads for AI systems and sales intelligence products.

---

## Products Featured in Strategy & Generation
1. **PodLeads AI**: YouTube lead-generation and sales-intelligence system for video-editing agencies, YouTube consultants, and podcast repurposing studios.
2. **Dental Sales Intelligence**: System researching dental practices, analyzing publicly observable digital signals (booking widgets, website technology, local hours) to identify outreach opportunities.
3. **Dental Operating System & AI Front Desk**: Operations & front-desk automation concept (strictly flagged so hypothetical capabilities are never claimed as live deployments).

---

## Key Capabilities

- **Zero-Hallucination & Anti-Slop Guardrails**: Eliminates generic influencer hyperbole (*"AI is transforming everything"*, fake metrics, emotional bait). Enforces 5-tier claim verification:
  1. *Verified facts*
  2. *Personal opinions & experiences*
  3. *Reasonable interpretations*
  4. *Unverified hypotheses*
  5. *Claims requiring user approval*
- **Official DeepSeek API Integration**: Server-side client with token usage accounting, estimated cost calculation in USD, timeout/retry resilience, and offline mock fallback.
- **6 Distinct Post Formats Per Idea**:
  - Concise Text Post
  - Personal Story / Builder's Lesson
  - Problem & Solution Post
  - Technical Breakdown for Business Owners
  - Demonstration-Led Post
  - Commercial Solution Spotlight
- **0–100 Buyer-Intent Scoring Engine**: Heuristic breakdown across Audience Relevance (20), Problem Specificity (20), Evidence & Credibility (20), Originality (15), Readability (10), Commercial Relevance (10), and CTA Quality (5).
- **10-Pillar Strategy & Content Calendar**: Generates 7-day or 30-day posting schedules with CSV export.
- **Multi-Format Export Pipelines**: One-click formatted LinkedIn clipboard copy, Markdown export, CSV schedule, and executive-grade PDF export (`fpdf2`) for individual posts or weekly content packs.
- **Performance Attribution Engine**: Logs 24h / 7d metrics, separates reach from conversation quality, and suggests strategic experiments.
- **Database Backup & Restore**: SQLite snapshot creation.

---

## Quickstart

### 1. Requirements
- Python 3.14+ (available via `py`)
- Node.js 20+ / npm (for frontend changes)

### 2. Configure Environment (Optional for Live DeepSeek API)
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
Add your official DeepSeek API key:
```env
DEEPSEEK_API_KEY=your_actual_deepseek_api_key
DEEPSEEK_MODEL=deepseek-chat
```
*(Note: If no API key is supplied, the application automatically runs in Offline Sandbox Mode with structured generation and mock token tracking).*

### 3. Start Application
Simply double-click `run_app.bat` or run:
```powershell
py -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
Then visit **http://127.0.0.1:8000** in your browser.

---

## Running Automated Tests
```powershell
py -m pytest backend/tests -v
```
All 20 unit and integration tests verify the database, DeepSeek fallback, heuristic scoring, PDF/CSV exports, and API endpoints.
