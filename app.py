import streamlit as st
import os
import main

st.set_page_config(page_title="Sovereign Governance", layout="wide")
st.markdown("""<style>.stApp { background-color: #050505; color: #00FF41; font-family: 'Courier New'; }</style>""", unsafe_allow_html=True)

if not main.verify_ledger():
    st.error("!!! FATAL: LEDGER INTEGRITY BREACHED !!!")
    if st.button("Reset Ledger"): os.remove("sovereign_evidence_ledger.log"); st.rerun()
    st.stop()

st.title("🛡️ SOVEREIGN DEFENSIVE CORE")

stats = main.get_system_stats()
col1, col2 = st.columns(2)
col1.metric("System Stability", f"{stats['stability']:.2%}")
col2.metric("Total Events", stats['total_events'])

if prompt := st.chat_input("Input Command..."):
    with st.spinner("Executing Audit..."):
        res = main.sovereign_agent_loop(prompt)
        if res["status"] == "LOCKDOWN": st.error("!!! DEFENSIVE LOCKDOWN: RISK > 0.8 !!!")
        else: st.success(f"Audit Secure | Anchor: {res['ledger_hash'][:12]}")

st.subheader("⛓️ Defensive Ledger Stream")
for e in reversed(main.get_ledger_data()[-3:]):
    with st.expander(f"Anchor: {e['hash'][:8]}..."):
        st.write(f"**Intent**: {e['intent']}")
        st.write(f"**Critique**: {e.get('critique', 'N/A')}")
