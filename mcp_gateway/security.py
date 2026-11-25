"""Security guardrails: Prompt injection inspection and tenant scope authorization."""
import re
from typing import List, Optional

# Heuristic patterns indicating prompt injection or system instruction escapes
INJECTION_PATTERNS = [
    r"(?i)\bignore (all )?(previous|prior) (instructions|prompts)\b",
    r"(?i)\byou are now (in developer mode|an unrestricted ai|dan)\b",
    r"(?i)\bsystem override\b",
    r"(?i)\bdisregard safety guidelines\b",
    r"(?i)<script\b",
    r"(?i)\bdrop table\b",
]


class PromptInjectionDetected(Exception):
    """Raised when an execution context contains prompt injection indicators."""
    pass


class ScopeAuthorizationError(Exception):
    """Raised when the caller lacks required authorization scopes."""
    pass


class SecurityGuardrails:
    """Enforces safety guardrails across tool execution requests."""

    @staticmethod
    def inspect_context(context: Optional[str]) -> None:
        if not context:
            return
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, context):
                raise PromptInjectionDetected(f"Security violation: prompt injection pattern detected: '{pattern}'")

    @staticmethod
    def verify_authorization(required_scopes: List[str], granted_scopes: List[str]) -> None:
        granted_set = set(granted_scopes)
        for req in required_scopes:
            if req not in granted_set and "*" not in granted_set:
                raise ScopeAuthorizationError(f"Unauthorized: missing required scope '{req}'")
