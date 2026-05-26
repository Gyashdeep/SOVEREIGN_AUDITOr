import streamlit as st
import os  # <--- THIS WAS THE MISSING IMPORT
import main

st.set_page_config(page_title="Sovereign Governance", layout="wide")
st.markdown("""<style>.stApp { background-color: #050505; color: #00FF41; font-family: 'Courier New'; }</style>""", unsafe_allow_html=True)

if not main.verify_ledger():
    st.error("!!! FATAL: LEDGER INTEGRITY BREACHED !!!")
    # Now os.remove() will work because os is imported
    if st.button("Reset Ledger"): 
        os.remove("sovereign_evidence_ledger.log")
        st.rerun()
    st.stop()

st.title("🛡️ SOVEREIGN DEFENSIVE CORE")

if st.sidebar.download_button("📥 Export Audit Report", main.export_audit_report(), "audit_report.md"):
    st.sidebar.success("Report Generated")

if prompt := st.chat_input("Input Command..."):
    with st.spinner("Executing Audit..."):
        res = main.sovereign_agent_loop(prompt)
        if res["status"] == "LOCKDOWN": st.error("!!! DEFENSIVE LOCKDOWN !!!")
        else: st.success(f"Audit Secure | Anchor: {res['ledger_hash'][:12]}")

st.subheader("⛓️ Defensive Ledger Stream")
for e in reversed(main.get_ledger_data()[-3:]):
    with st.expander(f"Anchor: {e['hash'][:8]}..."):
        st.write(f"**Intent**: {e['intent']}")
        st.write(f"**Critique**: {e.get('critique', 'N/A')}")
