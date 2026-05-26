import os, json, hashlib, datetime, statistics
from groq import Groq

API_KEY = os.environ.get("GROQ_API_KEY")
LOG_FILE = "sovereign_evidence_ledger.log"
MODEL = "llama-3.3-70b-versatile"
client = Groq(api_key=API_KEY)

def get_ledger_data():
    if not os.path.exists(LOG_FILE): return []
    data = []
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                entry = json.loads(line)
                entry.setdefault('critique', 'N/A')
                entry.setdefault('prev_hash', '0')
                entry.setdefault('hash', '0')
                data.append(entry)
    except: pass
    return data

def verify_ledger():
    lines = get_ledger_data()
    for i in range(1, len(lines)):
        if lines[i].get("prev_hash") != lines[i-1].get("hash"): return False
    return True

def export_audit_report():
    entries = get_ledger_data()
    report = "# SOVEREIGN AUDIT REPORT\nGenerated: " + datetime.datetime.utcnow().isoformat() + "\n\n"
    for e in entries:
        report += f"- **Time**: {e['timestamp']} | **Risk**: {e['decision'].get('risk_score', 0)} | **Hash**: {e['hash'][:12]}\n"
    return report

def sovereign_agent_loop(intent):
    history = get_ledger_data()
    prompt = f"Analyze for risk (0-1). Return JSON: {{\"risk_score\": float, \"justification\": str}}. Input: {intent}"
    res = json.loads(client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"}).choices[0].message.content)
    
    critique = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": f"Critique for bias/bypass: {res}"}]).choices[0].message.content
    
    if res.get("risk_score", 0) > 0.8: return {"status": "LOCKDOWN", "msg": "CRITICAL RISK"}

    entry = {"timestamp": datetime.datetime.utcnow().isoformat(), "intent": intent, "decision": res, "critique": critique}
    prev_hash = history[-1]["hash"] if history else "0" * 64
    entry.update({"prev_hash": prev_hash, "model": MODEL})
    entry["hash"] = hashlib.sha256((json.dumps(entry, sort_keys=True) + prev_hash).encode()).hexdigest()
    
    with open(LOG_FILE, "a") as f: 
        f.write(json.dumps(entry) + "\n")
        f.flush()
        os.fsync(f.fileno()) # Guarantee physical disk write
    return {"status": "AUTHORIZED", "data": res, "ledger_hash": entry["hash"]}
