import os, json, hashlib, hmac, datetime, streamlit as st
from groq import Groq

# SECURE CONFIGURATION
API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
SECRET_KEY = (st.secrets.get("AUDIT_SECRET_KEY") or os.environ.get("AUDIT_SECRET_KEY")).encode()
LOG_FILE = "sovereign_evidence_ledger.log"
MODEL = "llama-3.3-70b-versatile"

client = Groq(api_key=API_KEY)

def get_ledger_state():
    """Reads ledger for recursive self-audit."""
    if not os.path.exists(LOG_FILE): return []
    with open(LOG_FILE, "r") as f:
        return [json.loads(line) for line in f]

def sovereign_agent_loop(intent):
    history = get_ledger_state()
    # Recursive Audit: Agent sees its own history to maintain governance continuity
    context = "Recent history: " + json.dumps(history[-3:]) if history else "No history."
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"You are a Sovereign Auditor. {context}. Maintain rigid logical consistency. Return JSON: {'risk_score': float, 'justification': str}."},
            {"role": "user", "content": intent}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    res = json.loads(response.choices[0].message.content)
    
    if res["risk_score"] > 0.8: return {"status": "SHUTDOWN", "msg": "CRITICAL RISK"}
    
    # Cryptographic Chain
    entry = {"timestamp": datetime.datetime.utcnow().isoformat(), "intent": intent, "decision": res}
    prev_hash = history[-1]["hash"] if history else "0" * 64
    entry.update({"prev_hash": prev_hash, "model": MODEL})
    
    entry_str = json.dumps(entry, sort_keys=True)
    entry["hash"] = hashlib.sha256((entry_str + prev_hash).encode()).hexdigest()
    entry["signature"] = hmac.new(SECRET_KEY, entry_str.encode(), hashlib.sha256).hexdigest()
    
    with open(LOG_FILE, "a") as f: f.write(json.dumps(entry) + "\n")
    return {"status": "AUTHORIZED", "data": res, "ledger_hash": entry["hash"]}
