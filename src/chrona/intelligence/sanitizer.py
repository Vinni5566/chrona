import re
from typing import Dict, Any
from chrona.schemas.incident import Incident
from chrona.config.settings import settings

class Sanitizer:
    PATTERNS = {
        "api_key": re.compile(r'(?i)(?:key|token|secret|password|auth)[\s:=]+["\']?([a-zA-Z0-9_\-]{16,})["\']?'),
        "bearer": re.compile(r'(?i)bearer\s+([a-zA-Z0-9_\-\.]{20,})'),
        "email": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
        "ip": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    }

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        if not settings.CHRONA_ENABLE_SANITIZATION or not text:
            return text
            
        sanitized = text
        for name, pattern in cls.PATTERNS.items():
            for match in pattern.finditer(text):
                secret_value = match.group(0)
                sanitized = sanitized.replace(secret_value, f"***MASKED_{name.upper()}***")
        return sanitized

    @classmethod
    def sanitize_incident(cls, incident: Incident) -> Incident:
        if not settings.CHRONA_ENABLE_SANITIZATION:
            return incident
            
        incident.description = cls.sanitize_text(incident.description)
        if incident.logs:
            incident.logs = cls.sanitize_text(incident.logs)
            
        return incident

    @classmethod
    def sanitize_context(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        if not settings.CHRONA_ENABLE_SANITIZATION:
            return context
            
        sanitized = {}
        for k, v in context.items():
            if isinstance(v, str):
                sanitized[k] = cls.sanitize_text(v)
            elif isinstance(v, dict):
                sanitized[k] = cls.sanitize_context(v)
            elif isinstance(v, list):
                sanitized[k] = [cls.sanitize_text(i) if isinstance(i, str) else i for i in v]
            else:
                sanitized[k] = v
        return sanitized
