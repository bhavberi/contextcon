# DugOut — AI-Powered Franchise Management System

> An autonomous multi-agent system that runs the back-office of a sports/esports franchise — finding sponsors, monitoring vendors, tracking competitors, and protecting player brand deals — all powered by real-time B2B intelligence from Crustdata.
>
> Here, currently focused on cricket based IPL franchises, just to reduce the scope, but most of its parts are easily generalizable to other leagues, sports, and esports.

---

## The Problem

Running a sports or esports franchise involves a constant stream of high-stakes decisions with incomplete information:

- **Who should we approach for sponsorship?** And does this company conflict with a player's existing deals? Tracking the ever-changing corporate landscape manually is impossible.
- **Is our jersey/equipment supplier at risk?** We won't know until it's too late.
- **What is our rival franchise doing?** By the time we find out, they've already signed the deal, hired the coach, or poached the player.
- **How do we keep our sponsors engaged?** Personalised outreach requires research we don't have time to do.

Franchise operations teams are small, move fast, and are drowning in manual research. The intelligence exists — it just isn't accessible in real time.

Or otherwise they maintain a lower-tier "data analyst" role who scrapes news and LinkedIn for signals, but it's a reactive, noisy, and often too-late approach. The result? Missed opportunities, last-minute scrambles, and suboptimal deals.

---

## The Solution

**DugOut** is a multi-agent AI system where specialised agents handle each domain of franchise operations, all backed by live B2B data from Crustdata. It's not just a dashboard of insights — it's an autonomous operations system that turns signals into actions.

Each agent is purpose-built, autonomous, and actionable. They don't just surface information — they draft the email, flag the risk, score the deal, and tell you what to do next.

---

## The sub-agents

### Sponsorship Agent
Automates the entire sponsorship lifecycle.

- Discovers companies matching the franchise's target profile (industry, revenue band, growth stage) via Crustdata's Company API.
- Monitors target companies with Crustdata's Watcher API — when a prospect raises a Series B or changes their CMO, the agent drafts a personalised outreach automatically.
- **Player–Sponsor Fit Engine:**
  - *Auto mode:* Cross-references each player's existing sponsor roster, filters out brand competitors (e.g. a player signed with Puma cannot be recommended Adidas or Nike), and ranks remaining candidates by brand alignment.
  - *Score mode:* Enter any company name → live Crustdata enrichment → LLM returns a 0–10 compatibility score with structured Pros, Cons, and a one-paragraph rationale (not only based on industry but also brand values, recent news, and social sentiment).

### Supply Chain Agent
Real-time vendor risk monitoring with intelligent vendor discovery.

- All active vendors (merchandise, equipment, logistics) are watched continuously via Crustdata's Watcher API.
- The dashboard surfaces alerts ranked by severity — Critical, Warning, Watch — based on signals like headcount drops, leadership exits, or financial instability.
- Users can search for new vendors in plain English: *"Find a jersey supplier in South Asia with 200+ employees"* — a RAG-powered backend translates this into a precise Crustdata API call and returns ranked, vetted results.

### Competitor Intelligence Agent
Tracks rival franchises and turns raw signals into actions.

- Monitors competitor franchises and parent companies for key hires, new sponsorships, and structural changes.
- Aggregates the latest franchise news into a live feed via Crustdata's Web Search API.
- Generates a weekly Market Intelligence Brief — and crucially, adds an **Actionable Review**: concrete steps for managers derived from the week's competitive signals, not just a summary.

### Player PR / Social Agent
Maintains sponsor-aligned social presence without manual research.

- When a Watcher event fires (sponsor funding round, product launch, milestone), the agent drafts a social post for the relevant player that organically integrates the news.
- Exclusivity guard ensures content never references a competitor of an active sponsor.

---

## How It Works (Technical)

An "agent" is a Python function that:
1. Holds a system prompt defining its role.
2. Exposes a set of tool definitions (JSON schema) backed by Crustdata API wrappers.
3. Calls `anthropic.messages.create()` in a loop — Claude decides whether to return a response or invoke a tool, and the loop handles both.

---

## Role of Crustdata

Crustdata is the only B2B intelligence API that provides **live, structured data** on companies and people — not cached snapshots. For a franchise operations system, this matters:

- Sponsorship outreach that reacts to a funding round *this week*, not *last quarter*.
- Vendor risk alerts that fire when headcount drops *today*, not after a quarterly report.
- Competitor tracking that catches a key hire *the day it happens*.

The Watcher API is the backbone of the real-time layer — it turns DugOut from a research tool into an autonomous operations system.
