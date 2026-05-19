from chrona.scanner.secret_detector import SecretDetector

def test_secret_sanitization():
    text = 'Here is the api_key: "sk_live_1234567890abcdef123456" for use.'
    sanitized = SecretDetector.sanitize(text)
    
    assert "sk_live_1234567890abcdef123456" not in sanitized
    assert "***MASKED***" in sanitized
    assert SecretDetector.has_secrets(text) is True
