import os
import json
import hashlib
import hmac
import datetime
import anthropic
from groq import Groq

# --- CONFIGURATION ---
AUDIT_LOG_FILE = "sovereign_evidence_ledger.log"
SECRET_KEY = os.environ.get("AUDIT_SECRET_KEY", "prod-hardened-key-12345").encode()
CIRCUIT_THRESHOLD = 0.8 

# Initialize Clients
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# --- 1. MODEL ROUTING LAYER ---
def route_and_execute(intent_request, risk_profile):
    """
    Routes to specialized models based on risk and task complexity.
    - Low Risk: Groq (Llama-3.3-70B) for latency.
    - High Risk/Compliance: Claude 3.5 Sonnet for deep reasoning.
    """
    if risk_profile > 0.5:
        # Frontier Reasoning Engine
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system="You are a Sovereign Auditor. You are performing a high-stakes compliance verification. Output JSON only.",
            messages=[{"role": "user", "content": intent_request}]
        )
        return json.loads(response.content[0].text)
    else:
        # LPU-Powered Execution Engine
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a Sovereign Auditor. Output JSON only."},
                      {"role": "user", "content": intent_request}],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(response.choices[0].message.content)

# --- 2. CRYPTOGRAPHIC LEDGER ---
def append_to_ledger(entry):
    prev_hash = get_last_hash()
    entry["prev_hash"] = prev_hash
    entry_str = json.dumps(entry, sort_keys=True)
    entry["hash"] = hashlib.sha256((entry_str + prev_hash).encode()).hexdigest()
    entry["signature"] = hmac.new(SECRET_KEY, entry_str.encode(), hashlib.sha256).hexdigest()
    
    with open(AUDIT_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry["hash"]

def get_last_hash():
    if not os.path.exists(AUDIT_LOG_FILE): return "0" * 64
    with open(AUDIT_LOG_FILE, "r") as f:
        lines = f.readlines()
        return json.loads(lines[-1])["hash"] if lines else "0" * 64

# --- 3. AGENTIC LOOP ---
def sovereign_agent_loop(intent_request):
    # Preliminary triage to determine risk
    # (In a production system, use a small classification model here)
    risk_profile = 0.6 if "production" in intent_request.lower() else 0.2
    
    result = route_and_execute(intent_request, risk_profile)
    
    # Hard Circuit Breaker
    if result["risk_score"] > CIRCUIT_THRESHOLD:
        append_to_ledger({"event": "EMERGENCY_SHUTDOWN", "reason": "Risk threshold exceeded"})
        return "MODULE SHUTDOWN: SAFETY VIOLATION"
    
    # Human-in-the-Loop Intercept
    if 0.5 < result["risk_score"] <= CIRCUIT_THRESHOLD:
        print(f"\n[!!!] HITL ESCALATION: Action requires human approval.")
        if input("Authorize action? (y/n): ").lower() != 'y':
            append_to_ledger({"event": "ACTION_DENIED", "intent": intent_request})
            return "Action Denied by Operator"

    # Log to Cryptographic Ledger
    append_to_ledger({
        "timestamp": datetime.datetime.utcnow().isoformat(), 
        "intent": intent_request, 
        "decision": result
    })
    return "Action Authorized and Logged."

# Example Usage
print(sovereign_agent_loop("Modify database schema for production user data."))
