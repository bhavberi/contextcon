import os
import json
import google.generativeai as genai
from typing import List, Dict, Any

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
model = genai.GenerativeModel(model_name)

def draft_social_post(player_name: str, event_description: str, existing_sponsors: List[str], platforms: List[str] = ["Twitter", "Instagram", "LinkedIn"]) -> Dict[str, str]:
    """
    Draft social media posts for a player based on a sponsor event, ensuring no conflicts.
    """
    sponsors_info = ", ".join(existing_sponsors) if existing_sponsors else "None"
    
    prompt = f"""
    You are an expert PR and Social Media manager for the athlete: {player_name}.
    A recent event occurred related to a brand/sponsor: "{event_description}"
    
    Our player currently has active endorsement deals with the following brands: {sponsors_info}.
    CRITICAL EXCLUSIVITY GUARD: Ensure the drafted posts NEVER reference or inadvertently promote a direct competitor of any of these active sponsors. If the event itself is about a direct competitor, politely decline to draft the post or pivot it entirely to a neutral team-focused message.

    Draft engaging social media posts for {player_name} for the following platforms: {', '.join(platforms)}.
    Include relevant tags, emojis, and hashtags. Tailor the tone to each platform (e.g., professional for LinkedIn, visual/short for Instagram, conversational/quick for Twitter).
    
    Return your response EXACTLY as a JSON object where keys are the platform names and values are the drafted post text.
    Example:
    {{
      "Twitter": "Great news! ... #ad",
      "Instagram": "So proud to see... 📸✨",
      "LinkedIn": "I am thrilled to announce..."
    }}
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        print(f"Error drafting social post: {e}")
        return {platform: "Error generating post." for platform in platforms}

def draft_franchise_social_post(franchise_name: str, event_description: str, team_sponsors: List[str], platforms: List[str] = ["Twitter", "Instagram", "LinkedIn"]) -> Dict[str, str]:
    """
    Draft social media posts for the franchise account based on a sponsor event, ensuring no conflicts.
    """
    sponsors_info = ", ".join(team_sponsors) if team_sponsors else "None"
    
    prompt = f"""
    You are the official Social Media manager for the sports franchise: {franchise_name}.
    A recent event occurred related to a brand/sponsor: "{event_description}"
    
    The franchise currently has active partnership deals with the following brands: {sponsors_info}.
    CRITICAL EXCLUSIVITY GUARD: Ensure the drafted posts NEVER reference or inadvertently promote a direct competitor of any of these active team sponsors. 

    Draft engaging, official social media posts for the {franchise_name} official accounts for the following platforms: {', '.join(platforms)}.
    Include relevant tags, emojis, and hashtags. Tone should be official, exciting, and fan-centric.
    
    Return your response EXACTLY as a JSON object where keys are the platform names and values are the drafted post text.
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        print(f"Error drafting franchise post: {e}")
        return {platform: "Error generating post." for platform in platforms}

def analyze_opponent_post(opponent_team: str, post_content: str) -> Dict[str, Any]:
    """
    Analyze an opponent's social post for strategic insights and potential counter-messaging.
    """
    prompt = f"""
    You are a strategic intelligence analyst for a sports franchise.
    An opposing team, {opponent_team}, just posted the following on social media:
    "{post_content}"
    
    Analyze this post to identify any strategic updates, new sponsorships, roster changes, or shifts in messaging.
    
    Return your response EXACTLY as a JSON object with this schema:
    {{
        "key_takeaways": ["takeaway 1", "takeaway 2"],
        "sentiment": "Positive/Neutral/Negative",
        "actionable_insight": "What our franchise should do in response, if anything."
    }}
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        print(f"Error analyzing opponent post: {e}")
        return {
            "key_takeaways": ["Error analyzing post."],
            "sentiment": "Unknown",
            "actionable_insight": "None."
        }
