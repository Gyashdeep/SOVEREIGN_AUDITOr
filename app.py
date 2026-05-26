import streamlit as st
import os, json
from main import sovereign_agent_loop, verify_ledger, get_risk_analytics

st.set_page_config(page_title="Sovereign Governance", layout="wide")

st.markdown("""<style>
    .stApp { background-color: #050505; color: #00FF41; font-family: 'JetBrains Mono', monospace; }
</style>""", unsafe_allow_html=True)

if not verify_ledger():
    st.error("!!! FATAL: LEDGER INTEGRITY BREACHED !!!")
    st.stop()

st.title("🛡️ Sovereign Governance Core")

# Analytics Sidebar
metrics = get_risk_analytics()
st.sidebar.metric("System Stability", f"{1.0 - metrics['avg_risk']:.2%}")
st.sidebar.metric("Total Events", metrics['total_events'])

col1, col2 = st.columns([2, 1])

with col1:
    if prompt := st.chat_input("Enter Command..."):
        res = sovereign_agent_loop(prompt)
        if res["status"] == "SHUTDOWN": st.error(res["msg"])
        else: st.success(f"Audit Complete | Anchor: `{res['ledger_hash'][:16]}`")

with col2:
    st.subheader("⛓️ Ledger Stream")
    if os.path.exists("sovereign_evidence_ledger.log"):
        with open("sovereign_evidence_ledger.log", "r") as f:
            for line in reversed(f.readlines()[-5:]):
                e = json.loads(line)
                st.code(f"{e['hash'][:10]}... | Risk: {e['decision']['risk_score']}")
