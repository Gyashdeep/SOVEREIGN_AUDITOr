import streamlit as st
from main import (
    sovereign_agent_loop, 
    verify_ledger, 
    get_risk_analytics, 
    export_audit_report, 
    get_ledger_data
)

st.set_page_config(page_title="Sovereign Governance", layout="wide")

st.markdown("""<style>
    .stApp { background-color: #050505; color: #00FF41; font-family: 'JetBrains Mono', monospace; }
    .css-1r6slb0 { border: 1px solid #00FF41; }
</style>""", unsafe_allow_html=True)

# Verification Guardrail
if not verify_ledger():
    st.error("!!! FATAL: LEDGER INTEGRITY BREACHED !!!")
    st.stop()

st.title("🛡️ SOVEREIGN GOVERNANCE CORE")

# Dashboard Analytics
metrics = get_risk_analytics()
col_a, col_b, col_c = st.columns(3)
col_a.metric("Stability Rating", f"{1.0 - metrics['avg_risk']:.2%}")
col_b.metric("Total Transactions", metrics['total_events'])
col_c.download_button("📥 Export Audit Report", export_audit_report(), "audit_report.md")

# Governance Input
st.subheader("Input Command")
if prompt := st.chat_input("Enter Command..."):
    with st.spinner("Cryptographic Anchoring..."):
        res = sovereign_agent_loop(prompt)
        if res["status"] == "SHUTDOWN": st.error(res["msg"])
        else: st.success(f"Audit Complete | Anchor: `{res['ledger_hash'][:16]}`")

# Ledger View
st.subheader("⛓️ Ledger Stream")
for e in reversed(get_ledger_data()[-5:]):
    st.code(f"HASH: {e['hash'][:10]}... | RISK: {e['decision']['risk_score']}")
