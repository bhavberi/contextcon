import os
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

CRUSTDATA_API_KEY = os.getenv("CRUSTDATA_API_KEY")
BASE_URL = "https://api.crustdata.com"
HEADERS = {
    "authorization": f"Bearer {CRUSTDATA_API_KEY}",
    "content-type": "application/json",
    "x-api-version": "2025-11-01"
}

def search_companies(filters: Dict[str, Any], sorts: Optional[List[Dict[str, str]]] = None, limit: int = 10, fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Search for companies using the Crustdata Company Search API.
    """
    url = f"{BASE_URL}/company/search"
    payload = {
        "filters": filters,
        "limit": limit
    }
    if sorts:
        payload["sorts"] = sorts
    if fields:
        payload["fields"] = fields
    else:
        payload["fields"] = ["crustdata_company_id", "basic_info.name", "basic_info.primary_domain", "basic_info.industries"]

    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error in search_companies: {response.status_code} - {response.text}")
        return {"companies": []}

def enrich_companies(identifiers: List[Any], identifier_type: str = "crustdata_company_ids", fields: Optional[List[str]] = None, exact_match: Optional[bool] = None) -> Dict[str, Any]:
    """
    Enrich companies using the Crustdata Company Enrich API.
    Supports identifier types: crustdata_company_ids, domains, names, professional_network_profile_urls.
    """
    url = f"{BASE_URL}/company/enrich"
    payload = {
        identifier_type: identifiers
    }
    if fields:
        payload["fields"] = fields
    if exact_match is not None:
        payload["exact_match"] = exact_match
        
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error in enrich_companies: {response.status_code} - {response.text}")
        return {"results": []}

def identify_company(identifiers: List[str], identifier_type: str = "domains", exact_match: Optional[bool] = None) -> Dict[str, Any]:
    """
    Identify a company by various identifier types: domains, names, professional_network_profile_urls.
    """
    url = f"{BASE_URL}/company/identify"
    payload = {
        identifier_type: identifiers
    }
    if exact_match is not None:
        payload["exact_match"] = exact_match
        
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error in identify_company: {response.status_code} - {response.text}")
        return {"results": []}

def autocomplete_field(field: str, query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Get autocomplete suggestions for a given Company Search field.
    """
    url = f"{BASE_URL}/company/search/autocomplete"
    payload = {
        "field": field,
        "query": query,
        "limit": limit
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error in autocomplete_field: {response.status_code} - {response.text}")
        return {"suggestions": []}

def search_people(filters: Dict[str, Any], limit: int = 10, fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Search for people using the Crustdata Person Search API.
    """
    url = f"{BASE_URL}/person/search"
    payload = {
        "filters": filters,
        "limit": limit
    }
    if fields:
        payload["fields"] = fields
        
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error in search_people: {response.status_code} - {response.text}")
        return {"profiles": []}

