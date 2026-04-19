import os
import json
import google.generativeai as genai
from typing import Dict, Any, List
from tools.crustdata import search_companies

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
model = genai.GenerativeModel(model_name)

MOCK_VENDOR_EVENTS = [
    {
        "id": "v1",
        "vendor": "Global Equipment Support Ltd",
        "event": "Stock Price Crash & Layoffs",
        "description": "Stock price plummeted by 60% following a failed merger. Company announced immediate layoffs of 30% of its global workforce, affecting maintenance and support divisions.",
        "severity": "Critical",
        "impact": "High risk of delayed maintenance for stadium equipment and training gear. Potential service level agreement (SLA) breaches."
    },
    {
        "id": "v2",
        "vendor": "JerseyCraft Pro",
        "event": "Supply Chain Disruption in Manufacturing Hub",
        "description": "Primary manufacturing facility in New Jersey reported a major fire incident, halting production of all premium athletic wear for at least 3 months.",
        "severity": "Warning",
        "impact": "Potential shortage of official jerseys for the upcoming season. Delivery timelines for fans and players likely to be pushed back."
    }
]

def evaluate_vendor_risk(vendor_data: Dict[str, Any], recent_events: List[Dict[str, Any]]) -> str:
    """
    Evaluate vendor risk based on recent Watcher events.
    Returns severity: 'Critical', 'Warning', 'Watch', or 'Low'
    """
    if not recent_events:
        return "Low"
        
    prompt = f"""
    You are a supply chain risk analyst. Evaluate the risk level for the following vendor based on their recent events.
    
    Vendor: {vendor_data.get('company_name')}
    Recent Events: {recent_events}
    
    Assign one of the following risk levels:
    - Critical: High likelihood of immediate disruption (e.g., bankruptcy, massive layoffs, major leadership exodus).
    - Warning: Potential for near-term disruption (e.g., missed funding, steady headcount drop).
    - Watch: Minor signals to monitor (e.g., single executive departure).
    - Low: No concerning signals.
    
    Respond with ONLY the risk level word (Critical, Warning, Watch, or Low).
    """
    
    try:
        response = model.generate_content(prompt)
        level = response.text.strip()
        if level in ["Critical", "Warning", "Watch", "Low"]:
            return level
        return "Watch"
    except Exception as e:
        print(f"Error evaluating risk: {e}")
        return "Watch"

def search_vendors_rag(natural_language_query: str) -> List[Dict[str, Any]]:
    """
    Translate a natural language query into Crustdata Search API parameters and execute the search.
    """
    prompt = f"""
    You are an expert system that translates natural language requests into JSON parameters for the Crustdata Company Search API.
    
    User Query: "{natural_language_query}"
    
    Map this query into a JSON object containing the `filters` and optionally `sorts` fields.
    For example:
    {{
        "filters": {{
            "op": "and",
            "conditions": [
                {{"field": "basic_info.industries", "type": "in", "value": ["Apparel & Fashion"]}},
                {{"field": "locations.country", "type": "=", "value": "India"}},
                {{"field": "headcount.total", "type": "=>", "value": 200}}
            ]
        }},
        "sorts": [{{"column": "headcount.total", "order": "desc"}}]
    }}
    
    CRITICAL: For 'greater than or equal to', use '=>'. For 'less than or equal to', use '=<'.
    Use ONLY the following fields for filtering: 'basic_info.industries', 'locations.country', 'headcount.total'.
    
    CRITICAL: For 'greater than or equal to', use '=>'. For 'less than or equal to', use '=<'.
    Output ONLY valid JSON.
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        print("Model returned parameters:", text)
        api_params = json.loads(text)
        
        filters = api_params.get("filters")
        if not filters or not filters.get("conditions"):
             filters = {
                "op": "and",
                "conditions": [
                    {"field": "basic_info.industries", "type": "in", "value": ["Apparel & Fashion"]},
                    {"field": "locations.country", "type": "=", "value": "India"}
                ]
            }
            
        sorts = api_params.get("sorts")
        
        # Execute the search using the crustdata wrapper
        search_result = search_companies(filters=filters, sorts=sorts, limit=5)
        if "error" in search_result:
            print(f"Crustdata API Error: {search_result}")
        return search_result.get("companies", [])
        
    except Exception as e:
        print(f"Error in RAG vendor search: {e}")
        return []

def evaluate_vendors(candidates: List[Dict[str, Any]], region: str, product_specs: str, other_buyers: str) -> List[Dict[str, Any]]:
    """
    Evaluate a list of vendor candidates against specific criteria like region, product specs, and other buyers.
    """
    if not candidates:
        return []
        
    companies_info = "\n".join([f"- {c.get('basic_info', {}).get('name', 'Unknown')} (Domain: {c.get('basic_info', {}).get('primary_domain', 'N/A')})" for c in candidates])
    
    prompt = f"""
    You are a supply chain expert evaluating vendor candidates for a sports franchise.
    
    Our specific criteria:
    - Target Region: {region}
    - Product Specs: {product_specs}
    - Other Buyers (Trusted by): {other_buyers}
    
    Candidates:
    {companies_info}
    
    For each candidate, evaluate their potential fit based on their company profile and industry standing.
    
    Return your evaluation EXACTLY as a JSON array of objects with this schema:
    [
      {{
        "name": "Company Name",
        "score": 8,
        "reasoning": "Detailed explanation of why they fit or don't fit the criteria"
      }}
    ]
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        evaluations = json.loads(text)
        
        # Merge back into candidates
        result = []
        for c in candidates:
            name = c.get('basic_info', {}).get('name', '')
            score = 0
            reasoning = "No evaluation provided."
            for e in evaluations:
                if e.get("name") == name:
                    score = e.get("score", 0)
                    reasoning = e.get("reasoning", "")
                    break
            c["eval_score"] = score
            c["eval_reasoning"] = reasoning
            result.append(c)
            
        return sorted(result, key=lambda x: x.get("eval_score", 0), reverse=True)
    except Exception as e:
        print(f"Error evaluating vendors: {e}")
        for c in candidates:
            c["eval_score"] = 5
            c["eval_reasoning"] = "Error in AI evaluation."
        return candidates

def generate_risk_mitigation_suggestions(event_description: str, vendor_name: str) -> str:
    """
    Generate mitigation suggestions for a vendor risk event using a RAG approach.
    """
    # In a real RAG system, we would query a vector DB for 'Supply Chain Risk Mitigation' docs.
    # Here we simulate the retrieval context to show the user how it works.
    retrieved_context = """
    - Standard operating procedure for vendor insolvency: Immediate audit of inventory, activation of secondary vendors, and legal review of force majeure clauses.
    - Apparel supply chain disruption recovery: Lead times for jersey manufacturing average 8-12 weeks; alternative hubs in Vietnam and India are recommended for athletic wear.
    - Equipment maintenance risk: Critical equipment should have onsite spare parts (3-month buffer) and 24/7 support contracts with local third-party providers.
    """
    
    prompt = f"""
    You are a supply chain risk mitigation expert. A vendor risk event has been detected.
    
    Vendor: {vendor_name}
    Event Details: {event_description}
    
    Use the following retrieved best practices as context:
    {retrieved_context}
    
    Based on this, provide:
    1. **Risk Assessment**: A brief assessment of the business impact.
    2. **Mitigation Steps**: 3-4 specific, actionable mitigation steps.
    3. **RAG Search Query**: A suggested natural language query to use in our 'Vendor Discovery' tool to find replacements.
    4. **Alternative Vendor Categories**: Categories to filter by in Crustdata.
    
    Format your response in professional Markdown with clear headings.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating mitigation suggestions: {e}")
        return "Failed to generate suggestions. Please contact the supply chain department."

def find_alternative_vendors(event_description: str, vendor_name: str) -> Dict[str, Any]:
    """
    Generate search parameters for alternative vendors and execute the search.
    """
    # Hardcoded override for specific demo vendor
    if vendor_name == "Global Equipment Support Ltd":
        filters = {
            "op": "and",
            "conditions": [
                {"field": "basic_info.industries", "type": "in", "value": ["Industrial Machinery Manufacturing", "Machinery"]},
                {"field": "locations.country", "type": "=", "value": "IND"},
                {"field": "headcount.total", "type": "=>", "value": 100}
            ]
        }
        search_result = search_companies(filters=filters, limit=3)
        return {
            "query": "Find industrial machinery suppliers in IND",
            "params": {"filters": filters},
            "results": search_result.get("companies", [])
        }

    if vendor_name == "JerseyCraft Pro":
        filters = {
            "op": "and",
            "conditions": [
                {"field": "basic_info.industries", "type": "in", "value": ["Apparel & Fashion", "Textiles"]},
                {"field": "locations.country", "type": "=", "value": "IND"},
                {"field": "headcount.total", "type": "=>", "value": 50}
            ]
        }
        search_result = search_companies(filters=filters, limit=3)
        return {
            "query": "Find premium apparel manufacturers in IND",
            "params": {"filters": filters},
            "results": search_result.get("companies", [])
        }

    prompt = f"""
    You are a supply chain analyst. A key vendor, {vendor_name}, is facing a major risk: {event_description}.
    
    We need to find alternative vendors. 
    1. Identify the core industry and services provided by {vendor_name}.
    2. Generate a natural language search query to find replacements.
    3. Generate the EXACT JSON filter parameters for the Crustdata Company Search API.
    
    Use the following format:
    SEARCH_QUERY: [Your natural language query here]
    JSON_PARAMS: [Valid JSON object with 'filters' and optionally 'sorts']
    
    CRITICAL: For 'greater than or equal to', use '=>'. For 'less than or equal to', use '=<'.
    Fields: 'basic_info.industries', 'locations.country', 'headcount.total'.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # Parse the response
        search_query = ""
        json_params = {}
        
        if "SEARCH_QUERY:" in text:
            search_query = text.split("SEARCH_QUERY:")[1].split("JSON_PARAMS:")[0].strip()
        
        if "JSON_PARAMS:" in text:
            json_text = text.split("JSON_PARAMS:")[1].strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:-3].strip()
            elif json_text.startswith("```"):
                json_text = json_text[3:-3].strip()
            json_params = json.loads(json_text)
            
        # Execute search
        filters = json_params.get("filters")
        if not filters or not filters.get("conditions"):
            # Fallback filters if LLM failed to provide them
            filters = {
                "op": "and",
                "conditions": [
                    {"field": "basic_info.industries", "type": "in", "value": ["Apparel & Fashion"]},
                    {"field": "locations.country", "type": "=", "value": "USA"}
                ]
            }

        sorts = json_params.get("sorts")
        search_result = search_companies(filters=filters, sorts=sorts, limit=3)
        
        return {
            "query": search_query,
            "params": json_params,
            "results": search_result.get("companies", [])
        }
    except Exception as e:
        print(f"Error finding alternative vendors: {e}")
        return {"query": "Failed to generate search", "params": {}, "results": []}
