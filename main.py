import os, json, hashlib, hmac, datetime, streamlit as st
from groq import Groq

# SECURE CONFIGURATION
API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
SECRET_KEY = (st.secrets.get("AUDIT_SECRET_KEY") or os.environ.get("AUDIT_SECRET_KEY")).encode()
LOG_FILE = "sovereign_evidence_ledger.log"
MODEL = "llama-3.3-70b-versatile"

client = Groq(api_key=API_KEY)

def check_integrity():
    """Validates the cryptographic chain."""
    if not os.path.exists(LOG_FILE): return True
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
        for i in range(1, len(lines)):
            prev = json.loads(lines[i-1])
            curr = json.loads(lines[i])
            if curr["prev_hash"] != prev["hash"]: return False
    return True

def sovereign_agent_loop(intent):
    # Sentiment-adjusted audit
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a Sovereign Auditor. Focus on technical risk and logic. Ignore emotional tone. Return JSON: {'risk_score': float, 'justification': str}."},
            {"role": "user", "content": intent}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    res = json.loads(response.choices[0].message.content)
    
    if res["risk_score"] > 0.8: return {"status": "SHUTDOWN", "msg": "CRITICAL RISK"}
    
    # Sign and Chain
    entry = {"timestamp": datetime.datetime.utcnow().isoformat(), "intent": intent, "decision": res}
    prev_hash = "0"*64
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            if lines: prev_hash = json.loads(lines[-1])["hash"]
            
    entry.update({"prev_hash": prev_hash, "model": MODEL})
    entry_str = json.dumps(entry, sort_keys=True)
    entry["hash"] = hashlib.sha256((entry_str + prev_hash).encode()).hexdigest()
    entry["signature"] = hmac.new(SECRET_KEY, entry_str.encode(), hashlib.sha256).hexdigest()
    
    with open(LOG_FILE, "a") as f: f.write(json.dumps(entry) + "\n")
    return {"status": "AUTHORIZED", "data": res, "ledger_hash": entry["hash"]}
