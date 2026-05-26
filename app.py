import streamlit as st
import main

st.set_page_config(page_title="Sovereign Governance", layout="wide")
st.markdown("""<style>.stApp { background-color: #050505; color: #00FF41; font-family: 'Courier New'; }</style>""", unsafe_allow_html=True)

if not main.verify_ledger():
    st.error("!!! FATAL: LEDGER INTEGRITY BREACHED !!!")
    st.stop()

st.title("🛡️ SOVEREIGN DEFENSIVE CORE")

stats = main.get_system_stats()
col1, col2 = st.columns(2)
col1.metric("System Stability", f"{stats['stability']:.2%}")
col2.metric("Total Events", stats['total_events'])

if st.sidebar.download_button("📥 Export Audit Report", main.export_audit_report(), "audit_report.md"):
    st.sidebar.success("Report Generated")

if prompt := st.chat_input("Input Command..."):
    with st.spinner("Auditing..."):
        res = main.sovereign_agent_loop(prompt)
        if res["status"] == "LOCKDOWN": st.error("!!! DEFENSIVE LOCKDOWN !!!")
        else: st.success(f"Audit Secure | Anchor: {res['ledger_hash'][:12]}")

st.subheader("⛓️ Defensive Ledger Stream")
for e in reversed(main.get_ledger_data()[-3:]):
    with st.expander(f"Anchor: {e['hash'][:8]}..."):
        st.write(f"**Intent**: {e['intent']}")
        st.write(f"**Critique**: {e.get('critique', 'N/A')}")
