import json
import requests
import logging
from typing import Dict, Any
from chrona.config.settings import settings

class LLMClient:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def execute_task(self, model: str, task_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Call LLM API to get dynamic RCA."""
        memories_used = [m.get("memory").id for m in context.get("retrieved_memories", []) if m.get("score").status in ["fresh", "historical_useful"]]
        stale_memories_ignored = [m.get("memory").id for m in context.get("retrieved_memories", []) if m.get("score").status in ["stale", "dangerous"]]
        
        fallback_response = {
            "likely_root_cause": "System timeout or resource exhaustion.",
            "evidence": ["Could not fetch dynamic evidence due to LLM failure."],
            "suggested_remediation": ["Investigate logs manually.", "Check active deployments."],
            "risk_level": "High",
            "human_approval_required": True,
            "memories_used": memories_used,
            "stale_memories_ignored": stale_memories_ignored
        }

        if not self.api_key:
            logging.warning("GROQ_API_KEY not found. Using fallback mock response.")
            return fallback_response

        mem_str = "\n".join([f"- Memory ID {m.get('memory').id} ({m.get('score').status}): {m.get('memory').content} (Service: {m.get('memory').service})" 
                            for m in context.get("retrieved_memories", [])])
        incident_desc = context.get("incident", {}).get("description", "Unknown incident")
        
        prompt = f"""
You are a senior site reliability engineer analyzing a production incident.
Incident Description: {incident_desc}

Relevant Past Memories:
{mem_str}

Analyze the incident and memories. Determine the root cause, list evidence, suggest remediation steps, assign a risk level (Low/Medium/High/Critical), and state if human approval is required.

Return ONLY a raw JSON object with no markdown formatting. It must exactly match this schema:
{{
    "likely_root_cause": "string",
    "evidence": ["string", "string"],
    "suggested_remediation": ["string", "string"],
    "risk_level": "string",
    "human_approval_required": true/false
}}
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a senior SRE. Output only raw JSON. Never output markdown."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()
            
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            result = json.loads(content.strip())
            result["memories_used"] = memories_used
            result["stale_memories_ignored"] = stale_memories_ignored
            return result
            
        except Exception as e:
            logging.error(f"LLM call failed: {str(e)}")
            return fallback_response
