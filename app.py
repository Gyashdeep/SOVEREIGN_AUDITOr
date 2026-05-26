import streamlit as st
from main import (
    sovereign_agent_loop, 
    get_ledger_data, 
    export_audit_report, 
    verify_ledger
)

st.set_page_config(page_title="Sovereign Governance | DEFENSIVE", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #050505; color: #00FF41; font-family: 'Courier New'; }
</style>""", unsafe_allow_html=True)

# Integrity Check
if not verify_ledger():
    st.error("!!! FATAL: LEDGER INTEGRITY BREACHED !!!")
    st.stop()

st.title("🛡️ SOVEREIGN DEFENSIVE CORE")

# Side Controls
if st.sidebar.button("📥 Export Audit Report"):
    st.sidebar.download_button("Download Report", export_audit_report(), "audit_report.md")

# Input Processing
if prompt := st.chat_input("Input Command..."):
    with st.spinner("Executing Multi-Agent Audit..."):
        res = sovereign_agent_loop(prompt)
        if res["status"] == "LOCKDOWN": 
            st.error("!!! DEFENSIVE LOCKDOWN ENGAGED !!!")
        else: 
            st.success(f"Audit Secure | Anchor: {res['ledger_hash'][:12]}")

# Ledger Stream
st.subheader("⛓️ Defensive Ledger Stream")
for e in reversed(get_ledger_data()[-3:]):
    with st.expander(f"Anchor: {e['hash'][:8]}..."):
        st.write(f"**Intent**: {e['intent']}")
        st.write(f"**Critique**: {e['critique']}")
