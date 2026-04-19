import streamlit as st
import json
from agents.sponsorship import score_company, find_player_sponsors, discover_sponsors, evaluate_recommendations
from agents.supply_chain import (
    search_vendors_rag, 
    evaluate_vendor_risk, 
    evaluate_vendors, 
    MOCK_VENDOR_EVENTS, 
    generate_risk_mitigation_suggestions,
    find_alternative_vendors
)
from agents.competitor import (
    generate_market_intelligence_brief, 
    MOCK_NEWS_FEED, 
    get_automated_recommendations,
    find_partnership_leads,
    draft_partnership_email
)
from agents.social import draft_social_post, draft_franchise_social_post, analyze_opponent_post
from tools.crustdata import autocomplete_field

st.set_page_config(
    page_title="DugOut | Elite Franchise Management",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# --- HEADER SECTION ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try:
        st.image("assets/logo.png", width=150)
    except:
        st.title("🏏")

with col_title:
    st.markdown("<h1 class='dugout-title'>DUGOUT</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.2rem; margin-top: -15px; opacity: 0.7;'>Next-Gen AI Sports Franchise Operating System</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

if 'player_sponsors_cache' not in st.session_state:
    st.session_state['player_sponsors_cache'] = {}

tab1, tab2, tab3, tab4 = st.tabs(["🤝 Sponsorship", "📦 Supply Chain", "🕵️ Competitor Intel", "📱 Player PR / Social"])

# --- TAB 1: SPONSORSHIP ---
with tab1:
    st.markdown("### 🏟️ Player-Sponsor Fit Engine")
    
    # Load player data
    try:
        with open("rcb_players.json", "r") as f:
            player_data = json.load(f)
            players = player_data.get("players", [])
    except Exception:
        players = ["Virat Kohli", "Faf du Plessis"]

    col_sel, col_stat = st.columns([2, 1])
    with col_sel:
        selected_player = st.selectbox("Select Core Athlete", players)
        if st.button("Check Current Portfolio", use_container_width=True):
            with st.spinner(f"Retrieving global endorsements for {selected_player}..."):
                sponsors = find_player_sponsors(selected_player)
                if sponsors:
                    st.session_state['player_sponsors_cache'][selected_player] = sponsors
                    st.success(f"**Verified Portfolio for {selected_player}:** " + ", ".join(sponsors))
                else:
                    st.warning("No public sponsorship data available.")
    
    with col_stat:
        st.metric("Portfolio Depth", f"{len(st.session_state['player_sponsors_cache'].get(selected_player, []))}", "Verified")

    st.markdown("<div style='margin: 2rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);'></div>", unsafe_allow_html=True)
    
    col_disc, col_res = st.columns([1, 1.5])
    
    with col_disc:
        st.markdown("#### 🔍 Strategic Discovery")
        target_industry = st.text_input("Target Vertical", value="Apparel & Fashion", help="e.g. Fintech, Beverage, Luxury Goods")
        
        c1, c2 = st.columns(2)
        with c1:
            min_headcount = st.number_input("Min Headcount", value=500, min_value=1)
        with c2:
            target_country = st.text_input("Region (ISO-3)", value="USA")
            
        discover_context = st.text_area("Strategic Objectives", value="We are seeking high-growth consumer brands that align with Gen Z values.", height=100)
        discover_players = st.multiselect("Exclusivity Check Against:", players, default=[players[0]] if players else [])
        
        btn_discover = st.button("🚀 Run AI Discovery Engine", use_container_width=True)

    with col_res:
        st.markdown("#### 📊 Analysis Results")
        if btn_discover:
            with st.spinner("Enriching market data via Crustdata..."):
                existing_sponsors = set()
                for p in discover_players:
                    if p not in st.session_state['player_sponsors_cache']:
                        st.session_state['player_sponsors_cache'][p] = find_player_sponsors(p)
                    for s in st.session_state['player_sponsors_cache'][p]:
                        existing_sponsors.add(s)
                
                existing_sponsors_list = list(existing_sponsors)
                auto_res = autocomplete_field("basic_info.industries", target_industry, limit=1)
                exact_industry = target_industry
                if auto_res.get("suggestions"):
                    exact_industry = auto_res["suggestions"][0].get("value", target_industry)
                
                candidates = discover_sponsors([exact_industry], min_headcount=min_headcount, hq_country=target_country)
                recommendations = evaluate_recommendations(candidates, existing_sponsors_list, discover_context)
                
                if recommendations:
                    for rec in recommendations:
                        status_icon = "✅ Safe" if rec['is_safe'] else "⚠️ Conflict"
                        status_color = "#10b981" if rec['is_safe'] else "#ef4444"
                        st.markdown(f"""
                        <div class="rec-card" style="border-left-color: {status_color};">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h4 style="margin:0;">{rec['name']}</h4>
                                <span style="background: {status_color}33; color: {status_color}; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">{status_icon}</span>
                            </div>
                            <p style="margin: 10px 0; font-size: 0.9rem;">{rec['reasoning']}</p>
                            <div style="font-weight: bold; color: var(--gold);">Match Score: {rec['score']}/10</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No candidates matched your strategic filters.")
        else:
            st.info("Configure filters and click 'Run AI Discovery Engine' to see recommendations.")

    st.markdown("<div style='margin: 2rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);'></div>", unsafe_allow_html=True)
    
    st.markdown("#### 🎯 Rapid Prospect Scoring")
    c_score1, c_score2 = st.columns([1, 2])
    with c_score1:
        company_domain = st.text_input("Prospect Domain", placeholder="e.g. apple.com")
        if st.button("Generate Score Card", use_container_width=True):
            if company_domain:
                with st.spinner("Scoring prospect..."):
                    # Aggregate sponsors
                    existing_sponsors = set()
                    for p in players:
                        if p in st.session_state['player_sponsors_cache']:
                            for s in st.session_state['player_sponsors_cache'][p]:
                                existing_sponsors.add(s)
                    
                    result = score_company(company_domain, "Standard Evaluation", existing_sponsors=list(existing_sponsors))
                    st.session_state['last_score'] = result
            else:
                st.warning("Enter a domain.")
    
    with c_score2:
        if 'last_score' in st.session_state:
            res = st.session_state['last_score']
            if "error" in res:
                st.error(res["error"])
            else:
                st.metric("Compatibility Score", f"{res.get('score', 0)}/10")
                col_p, col_c = st.columns(2)
                with col_p:
                    st.markdown("🟢 **Strengths**")
                    for pro in res.get('pros', []): st.markdown(f"- {pro}")
                with col_c:
                    st.markdown("🔴 **Risks**")
                    for con in res.get('cons', []): st.markdown(f"- {con}")
                st.info(f"**Rationale:** {res.get('rationale', '')}")

# --- TAB 2: SUPPLY CHAIN ---
with tab2:
    st.markdown("### 📦 Supply Chain & Vendor Risk")
    
    st.markdown("#### 🔍 Intelligent Vendor Discovery")
    with st.container():
        nl_query = st.text_input("Strategic Sourcing Query", value="Find a sports apparel supplier in Asia with over 100 employees.")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            target_region = st.text_input("Region", value="Asia")
        with c2:
            product_specs = st.text_input("Material Specs", value="High-performance moisture-wicking fabric")
        with c3:
            other_buyers = st.text_input("Reference Clients", value="Major sports leagues")

        if st.button("Analyze Global Vendor Database", use_container_width=True):
            with st.spinner("Executing RAG-based vendor analysis..."):
                results = search_vendors_rag(nl_query)
                if results:
                    st.success(f"Discovered {len(results)} potential partners.")
                    evaluated_results = evaluate_vendors(results, target_region, product_specs, other_buyers)
                    for r in evaluated_results:
                        with st.expander(f"🏢 {r.get('basic_info', {}).get('name', 'Unknown')} - Fit: {r.get('eval_score', 0)}/10"):
                            st.markdown(f"**Domain:** {r.get('basic_info', {}).get('primary_domain', 'N/A')}")
                            st.info(f"**AI Evaluation:** {r.get('eval_reasoning', 'N/A')}")
                else:
                    st.warning("No vendors found matching these criteria.")
                
    st.markdown("<div style='margin: 2rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);'></div>", unsafe_allow_html=True)
    
    st.markdown("#### ⚠️ Operational Risk Monitor")
    st.markdown("Live signals from global logistics and manufacturing hubs.")

    for event in MOCK_VENDOR_EVENTS:
        sev_color = "#ef4444" if event['severity'] == "Critical" else "#f59e0b"
        st.markdown(f"""
        <div class="rec-card" style="border-left-color: {sev_color};">
            <div style="display: flex; justify-content: space-between;">
                <strong>{event['vendor']}</strong>
                <span style="color: {sev_color}; font-weight: bold;">{event['severity']}</span>
            </div>
            <div style="margin-top: 5px;">{event['event']}</div>
            <p style="font-size: 0.85rem; margin-top: 10px; opacity: 0.8;">{event['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        c_s, c_a = st.columns(2)
        with c_s:
            if st.button(f"Mitigate Risk", key=f"sugg_{event['id']}", use_container_width=True):
                with st.spinner("Generating strategy..."):
                    suggestions = generate_risk_mitigation_suggestions(event['description'], event['vendor'])
                    st.markdown(f"<div style='background: rgba(239, 68, 68, 0.1); padding: 1rem; border-radius: 8px;'>{suggestions}</div>", unsafe_allow_html=True)
        
        with c_a:
            if st.button(f"Source Alternatives", key=f"alt_{event['id']}", use_container_width=True):
                with st.spinner("Locating secondary vendors..."):
                    alt_data = find_alternative_vendors(event['description'], event['vendor'])
                    st.info(f"**AI Search Query:** {alt_data['query']}")
                    if alt_data['results']:
                        for res in alt_data['results']:
                            st.markdown(f"🔹 **{res.get('basic_info', {}).get('name', 'Unknown')}** ({res.get('basic_info', {}).get('primary_domain', 'N/A')})")
                    else:
                        st.warning("No immediate alternatives found.")

# --- TAB 3: COMPETITOR INTEL ---
with tab3:
    st.markdown("### 🕵️ Global Competitor Intelligence")
    
    col_news, col_rec = st.columns([1.5, 1])
    
    with col_news:
        st.markdown("#### 📰 Live Intelligence Stream")
        for news in MOCK_NEWS_FEED:
            with st.expander(f"{news['team']} | {news['title']}"):
                st.markdown(f"<span style='color: var(--primary); font-weight: bold;'>Type: {news['event_type']}</span>", unsafe_allow_html=True)
                st.write(news['description'])
                if st.button(f"Extract Strategic Signal", key=f"analyze_{news['id']}"):
                    st.markdown(f"""
                    <div class="signal-box">
                        <strong>🤖 AI Analysis:</strong> {news['analysis']}
                    </div>
                    """, unsafe_allow_html=True)

    with col_rec:
        st.markdown("#### ⚡ Watcher Actions")
        recs = get_automated_recommendations()
        for rec in recs:
            p_color = "#ef4444" if rec['priority'] == "High" else "#f59e0b" if rec['priority'] == "Medium" else "#10b981"
            st.markdown(f"""
            <div class="rec-card" style="border-left-color: {p_color};">
                <div style="color: {p_color}; font-weight: bold; text-transform: uppercase; font-size: 0.75rem; margin-bottom: 5px;">{rec['priority']} Priority</div>
                <div style="font-weight: bold; margin-bottom: 5px;">{rec['trigger']}</div>
                <div style="font-size: 0.9rem; margin-bottom: 10px;">Action: {rec['action']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Execute Outreach Flow", key=f"action_{rec['id']}"):
                st.session_state['active_rec'] = rec
        
        if 'active_rec' in st.session_state:
            rec = st.session_state['active_rec']
            st.markdown(f"#### 📧 Lead Gen: {rec['company']}")
            
            with st.spinner(f"Scraping decision-makers..."):
                leads = find_partnership_leads(rec['company'], rec['role'])
                if leads:
                    for i, lead in enumerate(leads):
                        with st.expander(f"👤 {lead['basic_profile']['name']} - {lead['basic_profile']['current_title']}"):
                            if st.button(f"Generate Personalized Pitch", key=f"email_{rec['id']}_{i}"):
                                with st.spinner("Drafting..."):
                                    email = draft_partnership_email(lead['basic_profile']['name'], rec['company'], rec['trigger'])
                                    st.text_area("Drafted Outreach", value=email, height=250)
                else:
                    st.warning("No leads found.")

    st.markdown("<div style='margin: 2rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);'></div>", unsafe_allow_html=True)
    st.markdown("#### 📜 Strategic Market Brief")
    if st.button("Synthesize Weekly Intelligence", use_container_width=True):
        with st.spinner("Processing signals..."):
            brief = generate_market_intelligence_brief()
            st.markdown(f"""
            <div class="rec-card" style="border-left: none; padding: 2rem;">
                {brief}
            </div>
            """, unsafe_allow_html=True)

# --- TAB 4: PLAYER PR / SOCIAL ---
with tab4:
    st.markdown("### 📱 Player PR & Social Command")
    
    col_social1, col_social2 = st.columns([1, 1.2])
    
    with col_social1:
        st.markdown("#### ✍️ AI Content Studio")
        account_type = st.radio("Publisher Profile", ["Player", "Franchise"])
        
        if account_type == "Player":
            social_player = st.selectbox("Athlete Select", players, key="social_player")
        else:
            franchise_name = st.text_input("Organization", value="Royal Challengers Bangalore")
            
        sponsor_event = st.text_area("Context/Event", value="Puma launches new limited edition gold spikes.", height=100)
        
        if st.button("Generate Synchronized Drafts", use_container_width=True):
            with st.spinner("Aligning with sponsor exclusivity guidelines..."):
                if account_type == "Player":
                    if social_player not in st.session_state['player_sponsors_cache']:
                        st.session_state['player_sponsors_cache'][social_player] = find_player_sponsors(social_player)
                    drafts = draft_social_post(social_player, sponsor_event, st.session_state['player_sponsors_cache'][social_player])
                else:
                    team_sponsors = ["Puma", "Qatar Airways"]
                    drafts = draft_franchise_social_post(franchise_name, sponsor_event, team_sponsors)
                
                st.session_state['current_social_drafts'] = drafts

    with col_social2:
        st.markdown("#### 📤 Multi-Platform Drafts")
        if 'current_social_drafts' in st.session_state:
            for platform, content in st.session_state['current_social_drafts'].items():
                with st.container():
                    st.markdown(f"**{platform}**")
                    st.info(content)
        else:
            st.info("Drafts will appear here after generation.")

    st.markdown("<div style='margin: 2rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);'></div>", unsafe_allow_html=True)
    
    st.markdown("#### 👁️ Rival Social Monitoring")
    
    c_rival1, c_rival2 = st.columns(2)
    with c_rival1:
        mock_opponent_posts = [
            {"team": "Mumbai Indians", "content": "Welcome aboard to our new global partner, Marriott Bonvoy!"},
            {"team": "Gujarat Titans", "content": "Strategic meeting today. Prep for the auction is on. 📈"}
        ]
        for post in mock_opponent_posts:
            with st.expander(f"Post from {post['team']}"):
                st.write(f"\"{post['content']}\"")
                if st.button(f"Analyze {post['team']}", key=f"btn_{post['team']}"):
                    st.session_state['rival_analysis'] = analyze_opponent_post(post['team'], post['content'])

    with c_rival2:
        if 'rival_analysis' in st.session_state:
            ra = st.session_state['rival_analysis']
            st.markdown("##### AI Rival Insights")
            st.metric("Sentiment", ra.get('sentiment', 'Neutral'))
            st.markdown("**Takeaways:**")
            for t in ra.get('key_takeaways', []): st.markdown(f"- {t}")
            st.warning(f"**Action:** {ra.get('actionable_insight', 'N/A')}")
