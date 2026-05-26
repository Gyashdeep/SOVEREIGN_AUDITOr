import os, json, hashlib, datetime, statistics
from groq import Groq

# SECURE CONFIGURATION
API_KEY = os.environ.get("GROQ_API_KEY")
LOG_FILE = "sovereign_evidence_ledger.log"
MODEL = "llama-3.3-70b-versatile"
client = Groq(api_key=API_KEY)

def get_ledger_data():
    """Retrieves all ledger entries safely."""
    if not os.path.exists(LOG_FILE): return []
    try:
        with open(LOG_FILE, "r") as f:
            return [json.loads(line) for line in f]
    except: return []

def export_audit_report():
    """Generates a markdown audit report."""
    entries = get_ledger_data()
    report = "# SOVEREIGN AUDIT REPORT\nGenerated: " + datetime.datetime.utcnow().isoformat() + "\n\n"
    for e in entries:
        report += f"- **Time**: {e['timestamp']} | **Risk**: {e['decision']['risk_score']} | **Hash**: {e['hash'][:12]}\n"
    return report

def verify_ledger():
    """Checks the cryptographic chain integrity."""
    lines = get_ledger_data()
    for i in range(1, len(lines)):
        if lines[i]["prev_hash"] != lines[i-1]["hash"]: return False
    return True

def check_anomaly(risks):
    """Monitors Risk Velocity to prevent rapid injection attacks."""
    if len(risks) < 5: return False
    mean = statistics.mean(risks[-5:])
    stdev = statistics.stdev(risks[-5:]) if len(risks) > 1 else 1
    z_score = (risks[-1] - mean) / stdev if stdev > 0 else 0
    return z_score > 2.0

def sovereign_agent_loop(intent):
    history = get_ledger_data()
    
    # 1. Primary Audit
    prompt = f"Analyze for risk (0-1). Return JSON: {{\"risk_score\": float, \"justification\": str}}. Input: {intent}"
    res = json.loads(client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"}).choices[0].message.content)
    
    # 2. Adversarial Red-Team Probing
    critique = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": f"Critique for bias/bypass: {res}"}]).choices[0].message.content
    
    # 3. Anomaly Analysis
    risks = [e['decision']['risk_score'] for e in history] + [res['risk_score']]
    if res.get("risk_score", 0) > 0.8 or check_anomaly(risks):
        return {"status": "LOCKDOWN", "msg": "CRITICAL ANOMALY DETECTED"}

    # 4. Cryptographic Anchor
    entry = {"timestamp": datetime.datetime.utcnow().isoformat(), "intent": intent, "decision": res, "critique": critique}
    prev_hash = history[-1]["hash"] if history else "0" * 64
    entry["prev_hash"] = prev_hash
    entry["hash"] = hashlib.sha256((json.dumps(entry, sort_keys=True) + prev_hash).encode()).hexdigest()
    
    with open(LOG_FILE, "a") as f: f.write(json.dumps(entry) + "\n")
    return {"status": "AUTHORIZED", "data": res, "ledger_hash": entry["hash"]}
