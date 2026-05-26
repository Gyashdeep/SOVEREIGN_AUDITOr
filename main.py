import os
import json
import hashlib
import hmac
import datetime
from groq import Groq

# Use os.environ to keep keys OUT of your code
API_KEY = os.environ.get("GROQ_API_KEY")
SECRET_KEY = os.environ.get("AUDIT_SECRET_KEY", "fallback-key").encode()
AUDIT_LOG_FILE = "sovereign_evidence_ledger.log"
MODEL = "openai/gpt-oss-120b"

client = Groq(api_key=API_KEY)

def route_and_execute(intent):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a Sovereign Auditor. Output JSON with 'risk_score' (0.0-1.0) and 'justification'."},
            {"role": "user", "content": intent}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    return json.loads(response.choices[0].message.content)

def append_to_ledger(entry):
    prev_hash = "0" * 64
    if os.path.exists(AUDIT_LOG_FILE):
        with open(AUDIT_LOG_FILE, "r") as f:
            lines = f.readlines()
            if lines: prev_hash = json.loads(lines[-1])["hash"]

    entry["prev_hash"] = prev_hash
    entry["model"] = MODEL
    entry_str = json.dumps(entry, sort_keys=True)
    entry["hash"] = hashlib.sha256((entry_str + prev_hash).encode()).hexdigest()
    entry["signature"] = hmac.new(SECRET_KEY, entry_str.encode(), hashlib.sha256).hexdigest()
    
    with open(AUDIT_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def sovereign_agent_loop(intent, approved=False):
    res = route_and_execute(intent)
    if res["risk_score"] > 0.8: return {"status": "SHUTDOWN", "msg": "Safety Breach."}
    if res["risk_score"] > 0.5 and not approved: return {"status": "PENDING", "data": res}
    append_to_ledger({"timestamp": datetime.datetime.utcnow().isoformat(), "intent": intent, "decision": res})
    return {"status": "AUTHORIZED", "data": res}
