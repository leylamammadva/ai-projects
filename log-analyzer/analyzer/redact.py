"""Pseudonymize sensitive values in log text BEFORE it is sent to a third-party LLM API.

- IPv4 addresses become PRIVATE_IP_n (RFC 1918, loopback, link-local) or PUBLIC_IP_n.
  The same address always gets the same token, so the model can still see repeated attempts
  and tell internal from external sources.
- E-mail addresses become EMAIL_n.
Limitation: usernames, hostnames and secrets in free text are NOT detected.
"""
import ipaddress
import re

IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
TOKEN = re.compile(r"\b(?:PRIVATE_IP|PUBLIC_IP|EMAIL)_\d+\b")

_INTERNAL = [
    ipaddress.ip_network(n)
    for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8", "169.254.0.0/16")
]


def _is_internal(ip) -> bool:
    return any(ip in net for net in _INTERNAL)


def redact(text: str) -> tuple[str, dict]:
    """Return (redacted_text, mapping token -> original value)."""
    mapping: dict[str, str] = {}
    seen: dict[str, str] = {}
    counters = {"PRIVATE_IP": 0, "PUBLIC_IP": 0, "EMAIL": 0}

    def token_for(value: str, kind: str) -> str:
        if value in seen:
            return seen[value]
        counters[kind] += 1
        token = f"{kind}_{counters[kind]}"
        seen[value] = token
        mapping[token] = value
        return token

    def ip_sub(match: re.Match) -> str:
        value = match.group(0)
        try:
            ip = ipaddress.ip_address(value)
        except ValueError:
            return value  # not a valid address (for example 999.1.1.1)
        return token_for(value, "PRIVATE_IP" if _is_internal(ip) else "PUBLIC_IP")

    text = EMAIL.sub(lambda m: token_for(m.group(0), "EMAIL"), text)
    text = IPV4.sub(ip_sub, text)
    return text, mapping


def restore(text: str, mapping: dict) -> str:
    """Put the original values back (used locally, only for display)."""
    return TOKEN.sub(lambda m: mapping.get(m.group(0), m.group(0)), text)
