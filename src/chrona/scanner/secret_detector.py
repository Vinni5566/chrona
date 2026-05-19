import re

class SecretDetector:
    PATTERNS = [
        re.compile(r'(?i)(api_key|secret|password|token)\s*[:=]\s*["\']?([a-zA-Z0-9\-_]{12,})["\']?'),
        re.compile(r'(?i)bearer\s+([a-zA-Z0-9\-\._]{20,})')
    ]

    @classmethod
    def sanitize(cls, text: str) -> str:
        if not text:
            return text
        sanitized = text
        for pattern in cls.PATTERNS:
            for match in pattern.finditer(text):
                # Ensure we have the capture group before replacing
                if match.lastindex:
                    secret_value = match.group(match.lastindex)
                    sanitized = sanitized.replace(secret_value, "***MASKED***")
        return sanitized

    @classmethod
    def has_secrets(cls, text: str) -> bool:
        if not text:
            return False
        for pattern in cls.PATTERNS:
            if pattern.search(text):
                return True
        return False
