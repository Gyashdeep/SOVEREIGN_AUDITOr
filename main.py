import os, json, hashlib, hmac, datetime, streamlit as st
from groq import Groq

# SECURE CONFIGURATION
API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
SECRET_KEY = (st.secrets.get("AUDIT_SECRET_KEY") or os.environ.get("AUDIT_SECRET_KEY")).encode()
LOG_FILE = "sovereign_evidence_ledger.log"
MODEL = "llama-3.3-70b-versatile"

client = Groq(api_key=API_KEY)

def verify_ledger():
    """Validates the entire chain-of-custody."""
    if not os.path.exists(LOG_FILE): return True
    with open(LOG_FILE, "r") as f:
        lines = [json.loads(line) for line in f]
    for i in range(1, len(lines)):
        if lines[i]["prev_hash"] != lines[i-1]["hash"]: return False
    return True

def sovereign_agent_loop(intent):
    history = [json.loads(line) for line in open(LOG_FILE, "r")] if os.path.exists(LOG_FILE) else []
    
    # SYSTEM PROMPT: Industry-grade strict JSON schema
    system_prompt = f"You are a Sovereign Auditor. Maintain rigid consistency. Return JSON: {{\"risk_score\": float, \"justification\": str}}."
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": intent}],
        response_format={"type": "json_object"},
        temperature=0
    )
    res = json.loads(response.choices[0].message.content)
    
    if res.get("risk_score", 0) > 0.8: return {"status": "SHUTDOWN", "msg": "CRITICAL RISK DETECTED"}
    
    # CHAIN ANCHORING
    entry = {"timestamp": datetime.datetime.utcnow().isoformat(), "intent": intent, "decision": res}
    prev_hash = history[-1]["hash"] if history else "0" * 64
    entry.update({"prev_hash": prev_hash, "model": MODEL})
    
    entry_str = json.dumps(entry, sort_keys=True)
    entry["hash"] = hashlib.sha256((entry_str + prev_hash).encode()).hexdigest()
    
    with open(LOG_FILE, "a") as f: f.write(json.dumps(entry) + "\n")
    return {"status": "AUTHORIZED", "data": res, "ledger_hash": entry["hash"]}
