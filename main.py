import os, json, hashlib, hmac, datetime, streamlit as st
from groq import Groq

# SECURE CONFIGURATION: Use st.secrets for production
API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
SECRET_KEY = (st.secrets.get("AUDIT_SECRET_KEY") or os.environ.get("AUDIT_SECRET_KEY")).encode()
LOG_FILE = "sovereign_evidence_ledger.log"
MODEL = "openai/gpt-oss-120b"

client = Groq(api_key=API_KEY)

def route_and_execute(intent):
    """Executes high-stakes reasoning via Flagship models."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a Sovereign Auditor. Output JSON: {'risk_score': float, 'justification': str}."},
            {"role": "user", "content": intent}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    return json.loads(response.choices[0].message.content)

def sign_and_chain(entry):
    """Creates a tamper-evident cryptographic chain."""
    prev_hash = "0" * 64
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            if lines: prev_hash = json.loads(lines[-1])["hash"]

    entry.update({"prev_hash": prev_hash, "model": MODEL})
    entry_str = json.dumps(entry, sort_keys=True)
    entry["hash"] = hashlib.sha256((entry_str + prev_hash).encode()).hexdigest()
    entry["signature"] = hmac.new(SECRET_KEY, entry_str.encode(), hashlib.sha256).hexdigest()
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry["hash"]

def sovereign_agent_loop(intent, approved=False):
    res = route_and_execute(intent)
    # The Circuit Breaker
    if res["risk_score"] > 0.8: return {"status": "SHUTDOWN", "msg": "CRITICAL RISK: Circuit Breaker Tripped."}
    if res["risk_score"] > 0.5 and not approved: return {"status": "PENDING", "data": res}
    
    sign_and_chain({"timestamp": datetime.datetime.utcnow().isoformat(), "intent": intent, "decision": res})
    return {"status": "AUTHORIZED", "data": res}
