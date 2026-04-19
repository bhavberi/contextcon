import os
import json
import google.generativeai as genai
from typing import List, Dict, Any
from tools.crustdata import search_companies, identify_company, enrich_companies

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
model = genai.GenerativeModel(model_name)

def discover_sponsors(target_industries: List[str], min_headcount: int = 50, hq_country: str = "USA") -> List[Dict[str, Any]]:
    """
    Find potential sponsors matching the franchise's criteria.
    """
    filters = {
        "op": "and",
        "conditions": [
            {"field": "basic_info.industries", "type": "in", "value": target_industries},
            {"field": "headcount.total", "type": "=>", "value": min_headcount},
            {"field": "locations.country", "type": "=", "value": hq_country}
        ]
    }
    sorts = [{"column": "headcount.total", "order": "desc"}]
    
    response = search_companies(filters=filters, sorts=sorts, limit=10)
    return response.get("companies", [])

def filter_competitors(candidate_companies: List[Dict[str, Any]], existing_sponsors: List[str]) -> List[Dict[str, Any]]:
    """
    Filter out direct competitors of existing sponsors using LLM.
    """
    if not existing_sponsors or not candidate_companies:
        return candidate_companies

    companies_info = "\n".join([f"- {c.get('basic_info', {}).get('name', 'Unknown')}" for c in candidate_companies])
    sponsors_info = ", ".join(existing_sponsors)
    
    prompt = f"""
    You are an expert sports marketing analyst.
    Our team currently has sponsorships with the following brands: {sponsors_info}.
    
    We are considering the following candidate companies for new sponsorships:
    {companies_info}
    
    Identify which of these candidate companies are DIRECT COMPETITORS to any of our existing sponsors.
    For example, if we are sponsored by Puma, Adidas and Nike are competitors.
    
    Return ONLY a comma-separated list of the names of the candidate companies that are safe to pursue (i.e., NOT competitors).
    If all are safe, list them all.
    """
    
    try:
        response = model.generate_content(prompt)
        safe_list = [name.strip().lower() for name in response.text.split(",")]
        
        filtered = []
        for c in candidate_companies:
            name = c.get('basic_info', {}).get('name', '').lower()
            if any(safe_name in name or name in safe_name for safe_name in safe_list):
                filtered.append(c)
        return filtered
    except Exception as e:
        print(f"Error filtering competitors: {e}")
        return candidate_companies

def evaluate_recommendations(candidate_companies: List[Dict[str, Any]], existing_sponsors: List[str], franchise_context: str) -> List[Dict[str, Any]]:
    """
    Evaluate a list of candidate companies against existing sponsors and franchise goals.
    Returns a list of recommendations with reasoning and safety flags.
    """
    if not candidate_companies:
        return []

    companies_info = "\n".join([f"- {c.get('basic_info', {}).get('name', 'Unknown')} (Domain: {c.get('basic_info', {}).get('primary_domain', 'N/A')})" for c in candidate_companies])
    sponsors_info = ", ".join(existing_sponsors) if existing_sponsors else "None"
    
    prompt = f"""
    You are a sports marketing expert. Evaluate the following candidate companies for a sponsorship deal.
    
    Franchise Goals: {franchise_context}
    Existing Player Sponsors (to avoid conflicts): {sponsors_info}
    
    Candidates:
    {companies_info}
    
    For each candidate, determine:
    1. If they are a DIRECT COMPETITOR to any existing player sponsors (Conflict = True).
    2. Why they are a good or bad fit for our franchise goals.
    3. A compatibility score (0-10).
    
    Return your evaluation EXACTLY as a JSON array of objects with this schema:
    [
      {{
        "name": "Company Name",
        "is_safe": true/false (false if it's a competitor),
        "reasoning": "Detailed explanation of fit or conflict",
        "score": 8
      }}
    ]
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        print(f"Error evaluating recommendations: {e}")
        return [{"name": c.get('basic_info', {}).get('name'), "is_safe": True, "reasoning": "Error in AI evaluation.", "score": 5} for c in candidate_companies]

def find_player_sponsors(player_name: str) -> List[str]:
    """
    Use Gemini to discover the current brand endorsements and sponsorships for a given player.
    """
    prompt = f"""
    You are a sports marketing expert.
    Please list the top current brand endorsements and sponsorships for the athlete: {player_name}.
    Return ONLY a comma-separated list of the brand names (e.g., Puma, MRF, Audi). 
    If you don't know any, return an empty string.
    """
    try:
        response = model.generate_content(prompt)
        brands = [brand.strip() for brand in response.text.split(",") if brand.strip()]
        return brands
    except Exception as e:
        print(f"Error finding player sponsors: {e}")
        return []

def score_company(company_domain: str, franchise_info: str, existing_sponsors: List[str] = None) -> Dict[str, Any]:
    """
    Live enrich a company and return a 0-10 compatibility score with pros/cons using Gemini.
    Penalizes the score if the company is a direct competitor to existing player sponsors.
    """
    id_response = identify_company([company_domain], "domains")
    
    if not isinstance(id_response, list) or not id_response:
        return {"error": "Company could not be identified (no response)."}
        
    first_result = id_response[0]
    if not first_result.get("matches"):
        return {"error": "Company could not be identified (no matches)."}
        
    company_data = first_result["matches"][0]["company_data"]
    
    sponsors_context = f"\nCRITICAL: Our players currently have active endorsement deals with the following brands: {', '.join(existing_sponsors)}.\nIf the candidate company is a DIRECT COMPETITOR to ANY of these existing player sponsors (e.g., Adidas is a competitor to Puma), you MUST give a very low compatibility score (e.g., 1-3) and explicitly list the conflict as a Major Con." if existing_sponsors else ""
    
    # 2. Score with Gemini
    prompt = f"""
    You are a sports franchise operations assistant assessing a potential sponsor.
    
    Franchise Context: {franchise_info}{sponsors_context}
    
    Company Data (from Crustdata):
    {company_data}
    
    Evaluate this company as a potential sponsor for our franchise.
    Output your response EXACTLY as a JSON object with the following schema:
    {{
        "score": <an integer between 0 and 10>,
        "pros": ["pro 1", "pro 2"],
        "cons": ["con 1", "con 2"],
        "rationale": "<A one-paragraph explanation of the score based on brand values and industry alignment>"
    }}
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        import json
        return json.loads(response.text)
    except Exception as e:
        return {"error": f"Failed to score company: {str(e)}"}
