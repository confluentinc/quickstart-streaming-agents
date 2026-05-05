"""Tool that fetches investigation context for an insurance claim from the CIS API."""

import json
import ssl
import urllib.request
import urllib.error

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

from ibm_watsonx_orchestrate.agent_builder.tools import tool

CIS_BASE_URL = "https://ildw2o0gik.execute-api.us-east-1.amazonaws.com/prod"


@tool(
    name="get_claim_investigation",
    description=(
        "Fetches the full investigation context for a single insurance claim from the "
        "Claims Investigation Service (CIS). Returns claim details, policy info, "
        "CLUE cross-insurer history, and identity verification results."
    ),
)
def get_claim_investigation(claim_id: str) -> dict:
    """Fetch investigation data for a claim from the CIS API.

    Args:
        claim_id: The claim identifier, e.g. '34102-03972'.

    Returns:
        Dict with claim details, policy info, CLUE history, and identity
        verification results. Returns an error dict if the claim is not found.
    """
    url = f"{CIS_BASE_URL}/investigation/{claim_id}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, context=_SSL_CTX, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"error": "Claim not found", "claim_id": claim_id}
        return {"error": f"CIS API error: HTTP {e.code}", "claim_id": claim_id}
    except Exception as e:
        return {"error": f"CIS API error: {e}", "claim_id": claim_id}
