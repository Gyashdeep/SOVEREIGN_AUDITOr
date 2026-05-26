import os
import json
import hashlib
import hmac
import datetime
from groq import Groq

AUDIT_LOG_FILE = "sovereign_evidence_ledger.log"
# Ensure your environment variable is set
SECRET_KEY = os.environ.get("AUDIT_SECRET_KEY", "prod-hardened-key-12345").encode()
CIRCUIT_THRESHOLD = 0.8
FLAGSHIP_MODEL = "openai/gpt-oss-120b"

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def route_and_execute(intent_request):
    """Uses Groq's most powerful flagship model for compliance reasoning."""
    response = groq_client.chat.completions.create(
        model=FLAGSHIP_MODEL,
        messages=[
            {"role": "system", "content": "You are a Sovereign Auditor. Perform compliance verification. Output ONLY JSON with 'risk_score' (float 0.0-1.0) and 'justification' (string)."},
            {"role": "user", "content": intent_request}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    return json.loads(response.choices[0].message.content)

def append_to_ledger(entry):
    prev_hash = get_last_hash()
    entry["prev_hash"] = prev_hash
    entry["model_used"] = FLAGSHIP_MODEL
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
    result = route_and_execute(intent_request)
    if result["risk_score"] > CIRCUIT_THRESHOLD:
        return {"status": "SHUTDOWN", "msg": "Safety Violation: Circuit Breaker Tripped."}
    if 0.5 < result["risk_score"] <= CIRCUIT_THRESHOLD and not approved:
        return {"status": "PENDING_APPROVAL", "data": result}
    
    append_to_ledger({"timestamp": datetime.datetime.utcnow().isoformat(), "intent": intent_request, "decision": result})
    return {"status": "AUTHORIZED", "data": result}

def verify_ledger(ledger_path, secret_key):
    if not os.path.exists(ledger_path): return False
    last_hash = "0" * 64
    with open(ledger_path, "r") as f:
        for line in f:
            entry = json.loads(line)
            actual_hash = entry.pop("hash")
            signature = entry.pop("signature")
            entry_str = json.dumps(entry, sort_keys=True)
            computed_hash = hashlib.sha256((entry_str + last_hash).encode()).hexdigest()
            computed_sig = hmac.new(secret_key, entry_str.encode(), hashlib.sha256).hexdigest()
            if computed_hash != actual_hash or not hmac.compare_digest(computed_sig, signature):
                return False
            last_hash = actual_hash
    return True
