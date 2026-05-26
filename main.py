import os
import json
import hashlib
import hmac
import datetime
import anthropic
from groq import Groq

AUDIT_LOG_FILE = "sovereign_evidence_ledger.log"
SECRET_KEY = os.environ.get("AUDIT_SECRET_KEY", "prod-hardened-key-12345").encode()
CIRCUIT_THRESHOLD = 0.8

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def route_and_execute(intent_request, risk_profile):
    if risk_profile > 0.5:
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system="You are a Sovereign Auditor. Output JSON only.",
            messages=[{"role": "user", "content": intent_request}]
        )
        return json.loads(response.content[0].text)
    else:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a Sovereign Auditor. Output JSON only."},
                      {"role": "user", "content": intent_request}],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(response.choices[0].message.content)

def append_to_ledger(entry):
    prev_hash = get_last_hash()
    entry["prev_hash"] = prev_hash
    entry_str = json.dumps(entry, sort_keys=True)
    entry["hash"] = hashlib.sha256((entry_str + prev_hash).encode()).hexdigest()
    entry["signature"] = hmac.new(SECRET_KEY, entry_str.encode(), hashlib.sha256).hexdigest()
    with open(AUDIT_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry["hash"]

def get_last_hash():
    if not os.path.exists(AUDIT_LOG_FILE): return "0" * 64
    with open(AUDIT_LOG_FILE, "r") as f:
        lines = f.readlines()
        return json.loads(lines[-1])["hash"] if lines else "0" * 64

def sovereign_agent_loop(intent_request, approved=False):
    risk_profile = 0.6 if "production" in intent_request.lower() else 0.2
    result = route_and_execute(intent_request, risk_profile)
    
    if result["risk_score"] > CIRCUIT_THRESHOLD:
        return {"status": "SHUTDOWN", "msg": "Safety Violation: Circuit Breaker Tripped."}
    
    if 0.5 < result["risk_score"] <= CIRCUIT_THRESHOLD and not approved:
        return {"status": "PENDING_APPROVAL", "data": result}
    
    append_to_ledger({"timestamp": datetime.datetime.utcnow().isoformat(), "intent": intent_request, "decision": result})
    return {"status": "AUTHORIZED", "data": result}
