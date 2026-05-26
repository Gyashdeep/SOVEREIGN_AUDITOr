import streamlit as st
import os, json
from main import sovereign_agent_loop, verify_ledger

st.set_page_config(page_title="Sovereign Governance", layout="wide")

st.markdown("""<style>
    .stApp { background-color: #050505; color: #00FF41; font-family: 'JetBrains Mono', monospace; }
    .status-bar { border: 1px solid #00FF41; padding: 10px; background: #000; margin-bottom: 20px; }
</style>""", unsafe_allow_html=True)

# Integrity Check
if not verify_ledger():
    st.error("FATAL: LEDGER INTEGRITY BREACHED. SYSTEM HALTED.")
    st.stop()

st.markdown('<div class="status-bar"><h2>🛡️ Sovereign Governance Core | Status: SECURE</h2></div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    if prompt := st.chat_input("Enter Command..."):
        with st.spinner("Processing Chain..."):
            res = sovereign_agent_loop(prompt)
            if res["status"] == "SHUTDOWN": st.error(res["msg"])
            else: st.success(f"Audit Complete | Anchor: `{res['ledger_hash'][:16]}`")

with col2:
    st.subheader("⛓️ Ledger Stream")
    if os.path.exists("sovereign_evidence_ledger.log"):
        with open("sovereign_evidence_ledger.log", "r") as f:
            lines = f.readlines()
            for line in reversed(lines[-5:]):
                entry = json.loads(line)
                st.code(f"{entry['hash'][:10]}... | Risk: {entry['decision']['risk_score']}")
