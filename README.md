# DugOut 🏏
### AI-Powered Multi-Agent Franchise Management System

**DugOut** is an autonomous multi-agent AI system designed to run the back-office operations of a sports or esports franchise. Powered by real-time B2B intelligence from **Crustdata**, it automates sponsorship discovery, vendor risk monitoring, competitor tracking, and player brand management.

While built to be generalizable, the current implementation is focused on **Indian Premier League (IPL)** franchises to demonstrate its depth in high-stakes sports management.

---

## 🚀 The Solution
Franchise operations teams are small and move fast. High-stakes decisions—like sponsorship deals or vendor selection—often rely on days of manual research. DugOut compresses this research into seconds by deploying specialized agents that turn raw signals into actionable operations.

### 🤖 The Sub-Agents

#### 🤝 Sponsorship Agent
*Automates the sponsorship lifecycle and ensures player-brand alignment.*
- **Discovery:** Finds companies matching specific profiles (revenue, growth, industry) via Crustdata's Company API.
- **Watcher Integration:** Triggers automated outreach drafts when a prospect raises funding or changes leadership.
- **Player-Sponsor Fit Engine:** 
    - *Auto Mode:* Automatically filters out competitors of a player's existing sponsors (e.g., Puma vs. Nike).
    - *Score Mode:* Provides a 0–10 compatibility score based on brand values, recent news, and sentiment.

#### 📦 Supply Chain Agent
*Real-time vendor risk monitoring and discovery.*
- **Risk Monitoring:** Continuously watches active vendors (merchandise, equipment, logistics) for headcount drops, leadership exits, or financial instability.
- **Natural Language Search:** Find new vendors using plain-English queries like *"Find a jersey supplier in South Asia with 200+ employees"*—backed by an LLM-to-API translation layer.

#### 🕵️ Competitor Intelligence Agent
*Tracks rival franchises to turn signals into strategy.*
- **Strategic Monitoring:** Tracks rivals for key hires, new sponsorships, and structural changes.
- **Market Intel Brief:** Aggregates news into a live feed and generates a weekly brief with a concrete **Actionable Review** for managers.

#### 📱 Player PR / Social Agent
*Maintains sponsor-aligned social presence automatically.*
- **Signal-to-Post:** Drafts social content for players when a sponsor hits a milestone (funding round, product launch).
- **Exclusivity Guard:** Ensures players never accidentally promote a competitor of an existing sponsor.
- **Opponent Watcher:** Monitors opponent social updates for strategic counter-messaging.

---

## 🛠️ Technical Stack
DugOut is built with a focus on speed, autonomy, and real-time data.

- **Core:** Python 3.12+
- **Brain:** **Google Gemini 2.5 Pro/Flash** for agentic reasoning and tool use.
- **Data Layer:** **Crustdata API** (Company API, Person Search API) for live, non-cached B2B intelligence. 
  - *Note:* Real-time Watcher APIs were unavailable during development; hence, a **Mock Watcher API** layer was implemented to simulate live event triggers.
- **Interface:** **Streamlit** dashboard for a premium, real-time management experience.
- **Architecture:** Custom autonomous agent loop (no heavy frameworks) for maximum control and transparency.

---

## 💎 Why Crustdata?
In professional sports, a week-old signal is already stale. Crustdata provides the only B2B intelligence API that delivers **live, structured data**:
- **Real-time:** Outreach that reacts to funding rounds *this week*.
- **Predictive:** Vendor risk alerts that fire when headcount drops *today*.
- **Accurate:** Competitor tracking that catches a key hire *the day it happens*.

---

## 🏁 Getting Started
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your `.env` with `CRUSTDATA_API_KEY` and `GOOGLE_API_KEY`.
4. Run the dashboard: `streamlit run franchise_mas/dashboard.py`