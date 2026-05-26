import os, json, hashlib, hmac, datetime, streamlit as st
from groq import Groq

# SECURE CONFIGURATION
API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
SECRET_KEY = (st.secrets.get("AUDIT_SECRET_KEY") or os.environ.get("AUDIT_SECRET_KEY")).encode()
LOG_FILE = "sovereign_evidence_ledger.log"
MODEL = "llama-3.3-70b-versatile" 

client = Groq(api_key=API_KEY)

def route_and_execute(intent):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a Sovereign Auditor. You analyze intent for risk. Return ONLY JSON: {'risk_score': 0.0, 'justification': '...'}"},
            {"role": "user", "content": intent}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    return json.loads(response.choices[0].message.content)

def sign_and_chain(entry):
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

def sovereign_agent_loop(intent):
    res = route_and_execute(intent)
    
    if res["risk_score"] > 0.8:
        return {"status": "SHUTDOWN", "msg": "CRITICAL RISK: Circuit Breaker Tripped."}
    
    # Secure logging
    ledger_hash = sign_and_chain({"timestamp": datetime.datetime.utcnow().isoformat(), "intent": intent, "decision": res})
    return {"status": "AUTHORIZED", "data": res, "ledger_hash": ledger_hash}
