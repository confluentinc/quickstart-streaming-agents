#!/usr/bin/env python3
"""
WatsonX Orchestrate BFF Chat Client
=====================================
Calls the Orchestrate agent via the UI's backend-for-frontend (BFF) API.
Auth uses browser session cookies (NOT IAM bearer tokens).

Usage:
  python3 scripts/wxo_chat.py "Your message here"

Cookie refresh:
  The session cookies are valid ~24h from browser login. To refresh:
  1. Open browser DevTools → Network
  2. Send a message in the Orchestrate chat UI
  3. Copy cookies + X-IBM-WO-CSRF from the /runs request
  4. Update SESSION_COOKIES and CSRF_TOKEN below, or set env vars.

CSRF token derivation (likely SHA-256 of __Secure-fgp cookie value as a string):
  import hashlib; print(hashlib.sha256(fgp.encode()).hexdigest())
"""

import json
import sys
import os
import uuid
import hashlib
import urllib.request
import urllib.error

# ── Configuration ─────────────────────────────────────────────────────────────

BFF_BASE = "https://us-south.watson-orchestrate.cloud.ibm.com/mfe_home_archer/api/v1"
AGENT_ID = "cb1a593b-2b00-4fd4-b956-39483cc5bfaf"

# Key session cookies from browser (update when session expires)
SESSION_ID = os.environ.get("WXO_SESSION_ID", "1e86aa7f-3af4-408f-99f2-80f4c7dd581a")
FGP = os.environ.get("WXO_FGP", "6f290aa72af20e3c645a0597bfaa14148cdbab3140c0b4d59aefdb4f56dc820fab0c723698d8693fb418bb64b5624f7fefa5")
TENANT_ID = os.environ.get("WXO_TENANT_ID", "e092751eddca4504a02e59688bb35059_9a0991cf-de28-48c9-9fd3-d109e3051dbb")
IAM_COOKIE = os.environ.get("WXO_IAM_COOKIE", "eyJhbGciOiJpYyJ9.eyJzZXNzaW9uX2lkIjoiQy1kZDk4MDYzNS0yZjJjLTQ0NGQtYmRjOS04OWMyMDAzYzNlZmYiLCJpYW1faWQiOiJJQk1pZC02OTYwMDFJSEhTIiwiYWNjb3VudF9pZCI6ImUwOTI3NTFlZGRjYTQ1MDRhMDJlNTk2ODhiYjM1MDU5In0.gZK5AvIhCquLFEkmyNY7XIYsViI2VMSiJ8u6cur9v_U7KPaeam1f-JS_rbwZsVRuzA6rm2dbcWxJjru_nDLuw4oKXFReSeSSYaLh9MaEqosLSv3w7qIQpIDodn1P8r5VrF08u5J723cEe_BXZFZVH5oIFMXRdAzuGZrpOoSAQrJQcL2Q85_6tX9AlhJ7u6mg8oCreKN2-kXHEpDbXZBPAT217lPv5dyC9w5sBYBIEHRRuIQSZN34nh9j9Q18Il12hqCTsLfqhkfG0xT_zMeUxoFwprNrXGCZ5T9Z7meDDzuIB_sxgxy7ty4DMtFECDHdlIQhbqSPD7BtBtTgLJNxydWV26R4InV_-YTed9NqhYYxfUVZe7ukxzCnxauExSL6YwvmLgzJMYztq3lpLK4UNwO4FPzepG3PjCEsMiVyt9TMRPsMqU7Ev4TtTGBAkGKnRIoCT2KxlPs9orRDWU3c6SbObKiYx8nVBbqiT-3DHTrcrd6iEGH8zaramraeHEUpAuTqG_4rnm7r-Km7J2YY2YqvAquSW6fglUzF3auaU16nbm-lI5woZbiTjXvA0ghUA61pUKX3jN7r3TJp-7it7yFeX_hF3CJGwcibM6yKq3bM0g")
CRN = "crn:v1:bluemix:public:watsonx-orchestrate:us-south:a/e092751eddca4504a02e59688bb35059:9a0991cf-de28-48c9-9fd3-d109e3051dbb::"

# ── CSRF computation ───────────────────────────────────────────────────────────

def compute_csrf(fgp: str) -> str:
    """The CSRF token appears to be SHA-256 of the __Secure-fgp cookie value."""
    return hashlib.sha256(fgp.encode()).hexdigest()

# ── Cookie helpers ─────────────────────────────────────────────────────────────

def make_cookie_header(session_id: str, fgp: str, tenant_id: str) -> str:
    """Minimal cookie set needed for the BFF API."""
    return (
        f"x-ibm-wo-session-id={session_id}; "
        f"__Secure-fgp={fgp}; "
        f"x-ibm-wo-tenant-id={tenant_id}; "
        f"com.ibm.cloud.iam.iamcookie.prod={IAM_COOKIE}; "
        f"crn={CRN}"
    )

def parse_set_cookie(headers) -> dict:
    """Extract session cookies from Set-Cookie headers."""
    cookies = {}
    for header in headers.get_all("set-cookie") or []:
        name, _, rest = header.partition("=")
        value, _, _ = rest.partition(";")
        cookies[name.strip()] = value.strip()
    return cookies

# ── API calls ──────────────────────────────────────────────────────────────────

def create_thread(message_content: str, session_id: str, fgp: str, tenant_id: str) -> tuple[str, str, str]:
    """
    POST /v1/threads
    Returns (thread_id, new_session_id, new_fgp)
    """
    csrf = compute_csrf(fgp)
    cookie = make_cookie_header(session_id, fgp, tenant_id)
    url = f"{BFF_BASE}/threads"
    body = json.dumps({"title": message_content}).encode()

    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-IBM-WO-CSRF", csrf)
    req.add_header("x-ibm-request-id", str(uuid.uuid4()))
    req.add_header("Cookie", cookie)
    req.add_header("Origin", "https://us-south.watson-orchestrate.cloud.ibm.com")

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
        thread_id = data["thread_id"]
        new_cookies = parse_set_cookie(resp.headers)
        new_session_id = new_cookies.get("x-ibm-wo-session-id", session_id)
        new_fgp = new_cookies.get("__Secure-fgp", fgp)
        new_tenant_id = new_cookies.get("x-ibm-wo-tenant-id", tenant_id)
        print(f"  [thread] Created: {thread_id}", flush=True)
        return thread_id, new_session_id, new_fgp, new_tenant_id


def send_message(message_content: str, thread_id: str, session_id: str, fgp: str, tenant_id: str) -> str:
    """
    POST /v1/orchestrate/runs?stream=true&...
    Reads SSE and returns the full assistant message text from message.created event.
    """
    csrf = compute_csrf(fgp)
    cookie = make_cookie_header(session_id, fgp, tenant_id)
    url = f"{BFF_BASE}/orchestrate/runs?stream=true&stream_timeout=180000&multiple_content=true"

    payload = {
        "message": {"role": "user", "content": message_content},
        "additional_properties": {},
        "context": {},
        "agent_id": AGENT_ID,
        "thread_id": thread_id,
    }
    body = json.dumps(payload).encode()

    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-IBM-WO-CSRF", csrf)
    req.add_header("x-ibm-request-id", str(uuid.uuid4()))
    req.add_header("x-watson-channel", "agentic_chat")
    req.add_header("Cookie", cookie)
    req.add_header("Origin", "https://us-south.watson-orchestrate.cloud.ibm.com")

    with urllib.request.urlopen(req, timeout=180) as resp:
        # SSE: each line is a JSON object (not "data: ..." prefixed in this API)
        full_text = ""
        for raw_line in resp:
            line = raw_line.decode("utf-8").strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            event_type = event.get("event")
            if event_type == "run.step.intermediate":
                msg = event.get("data", {}).get("message", {}).get("text", "")
                if msg:
                    print(f"  [step] {msg}", flush=True)
            elif event_type == "message.delta":
                # Streaming token chunks — print dots to show progress
                print(".", end="", flush=True)
            elif event_type == "message.created":
                # Full assembled message — use this as the final response
                print()  # newline after dots
                content_blocks = event.get("data", {}).get("message", {}).get("content", [])
                full_text = " ".join(
                    b.get("text", "") for b in content_blocks if b.get("response_type") == "text"
                )
            elif event_type in ("run.completed", "done"):
                break

    return full_text


# ── Main ───────────────────────────────────────────────────────────────────────

def chat(message: str) -> str:
    """Full two-step flow: create thread → send message → return response."""
    session_id = SESSION_ID
    fgp = FGP
    tenant_id = TENANT_ID

    print(f"Creating thread...", flush=True)
    thread_id, session_id, fgp, tenant_id = create_thread(message, session_id, fgp, tenant_id)

    print(f"Sending message to agent {AGENT_ID}...", flush=True)
    response = send_message(message, thread_id, session_id, fgp, tenant_id)

    return response


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/wxo_chat.py 'Your message here'")
        print("\nExample:")
        print('  python3 scripts/wxo_chat.py "Investigate claim 34102-04116"')
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    print(f"\nMessage: {message}\n")

    try:
        response = chat(message)
        print(f"\n{'='*60}")
        print("Agent response:")
        print('='*60)
        print(response)
    except urllib.error.HTTPError as e:
        print(f"\nHTTP {e.code}: {e.read().decode()}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        raise
