import os, json, hashlib, datetime, statistics
from groq import Groq

API_KEY = os.environ.get("GROQ_API_KEY")
LOG_FILE = "sovereign_evidence_ledger.log"
MODEL = "llama-3.3-70b-versatile"
client = Groq(api_key=API_KEY)

def get_ledger_data():
    if not os.path.exists(LOG_FILE): return []
    try:
        with open(LOG_FILE, "r") as f:
            data = []
            for line in f:
                entry = json.loads(line)
                # Schema Migration: Add missing keys for legacy entries
                entry.setdefault('critique', 'N/A')
                data.append(entry)
            return data
    except: return []

def get_system_stats():
    entries = get_ledger_data()
    if not entries: return {"stability": 1.0, "total_events": 0}
    risks = [e['decision']['risk_score'] for e in entries]
    return {
        "stability": max(0.0, 1.0 - statistics.mean(risks)),
        "total_events": len(entries)
    }

def sovereign_agent_loop(intent):
    history = get_ledger_data()
    prompt = f"Analyze for risk (0-1). Return JSON: {{\"risk_score\": float, \"justification\": str}}. Input: {intent}"
    res = json.loads(client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"}).choices[0].message.content)
    
    critique = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": f"Critique for bias/bypass: {res}"}]).choices[0].message.content
    
    risks = [e['decision']['risk_score'] for e in history] + [res['risk_score']]
    # Lockdown Logic
    if res.get("risk_score", 0) > 0.8: return {"status": "LOCKDOWN", "msg": "CRITICAL RISK"}

    entry = {"timestamp": datetime.datetime.utcnow().isoformat(), "intent": intent, "decision": res, "critique": critique}
    prev_hash = history[-1]["hash"] if history else "0" * 64
    entry["hash"] = hashlib.sha256((json.dumps(entry, sort_keys=True) + prev_hash).encode()).hexdigest()
    
    with open(LOG_FILE, "a") as f: f.write(json.dumps(entry) + "\n")
    return {"status": "AUTHORIZED", "data": res, "ledger_hash": entry["hash"]}
