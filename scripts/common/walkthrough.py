"""Shared patterns for the email placeholder in LAB1-Walkthrough.md."""

import re

EMAIL_PLACEHOLDER = "<<YOUR-EMAIL-ADDRESS-HERE>>"

# Matches the placeholder or a previously injected email address, but nothing else,
# so prose such as "`EMAIL RECIPIENT:` line" is left untouched.
_EMAIL_TOKEN = r"(?:<<YOUR-EMAIL-ADDRESS-HERE>>|[^\s`'<>]+@[^\s`'<>]+)"

EMAIL_PATTERNS = (
    re.compile(rf'(The "to" parameter must be a single string value:[ \t]*){_EMAIL_TOKEN}'),
    re.compile(rf"(EMAIL RECIPIENT:[ \t]*){_EMAIL_TOKEN}"),
)


def replace_email(text: str, replacement: str) -> str:
    """Replace the placeholder (or any injected email) with `replacement`."""
    for pattern in EMAIL_PATTERNS:
        text = pattern.sub(lambda m: m.group(1) + replacement, text)
    return text
