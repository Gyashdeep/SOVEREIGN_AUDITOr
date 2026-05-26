import os, json, hashlib, hmac, datetime
from groq import Groq

# SECURE CONFIGURATION
API_KEY = os.environ.get("GROQ_API_KEY")
SECRET_KEY = os.environ.get("AUDIT_SECRET_KEY", "default_secret").encode()
LOG_FILE = "sovereign_evidence_ledger.log"
MODEL = "llama-3.3-70b-versatile"

client = Groq(api_key=API_KEY)

def get_ledger_data():
    if not os.path.exists(LOG_FILE): return []
    with open(LOG_FILE, "r") as f:
        return [json.loads(line) for line in f]

def get_risk_analytics():
    entries = get_ledger_data()
    if not entries: return {"avg_risk": 0.0, "total_events": 0}
    risks = [e['decision']['risk_score'] for e in entries]
    return {"avg_risk": sum(risks)/len(risks), "total_events": len(entries)}

def export_audit_report():
    entries = get_ledger_data()
    report = "# SOVEREIGN AUDIT REPORT\n"
    report += f"Generated: {datetime.datetime.utcnow().isoformat()}\n\n"
    for e in entries:
        report += f"- **Time**: {e['timestamp']} | **Risk**: {e['decision']['risk_score']} | **Hash**: {e['hash'][:12]}\n"
    return report

def verify_ledger():
    lines = get_ledger_data()
    for i in range(1, len(lines)):
        if lines[i]["prev_hash"] != lines[i-1]["hash"]: return False
    return True

def sovereign_agent_loop(intent):
    history = get_ledger_data()
    system_prompt = f"You are a Sovereign Auditor. Maintain rigid consistency. Return JSON: {{\"risk_score\": float, \"justification\": str}}."
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": intent}],
        response_format={"type": "json_object"},
        temperature=0
    )
    res = json.loads(response.choices[0].message.content)
    
    if res.get("risk_score", 0) > 0.8: return {"status": "SHUTDOWN", "msg": "CRITICAL RISK - NOTIFICATION TRIGGERED"}
    
    entry = {"timestamp": datetime.datetime.utcnow().isoformat(), "intent": intent, "decision": res}
    prev_hash = history[-1]["hash"] if history else "0" * 64
    entry.update({"prev_hash": prev_hash, "model": MODEL})
    
    entry_str = json.dumps(entry, sort_keys=True)
    entry["hash"] = hashlib.sha256((entry_str + prev_hash).encode()).hexdigest()
    
    with open(LOG_FILE, "a") as f: f.write(json.dumps(entry) + "\n")
    return {"status": "AUTHORIZED", "data": res, "ledger_hash": entry["hash"]}
