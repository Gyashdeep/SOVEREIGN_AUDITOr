import os
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

import streamlit as st
import main

st.set_page_config(page_title="Sovereign Governance", layout="wide")
st.markdown("""<style>.stApp { background-color: #050505; color: #00FF41; font-family: 'Courier New'; }</style>""", unsafe_allow_html=True)

if "ledger_checked" not in st.session_state:
    st.session_state.is_valid = main.verify_ledger()
    st.session_state.ledger_checked = True

if not st.session_state.is_valid:
    st.error("!!! FATAL: LEDGER INTEGRITY BREACHED !!!")
    if st.button("RESET CORE"):
        if os.path.exists(main.LOG_FILE): os.remove(main.LOG_FILE)
        st.session_state.is_valid = True
        st.rerun()
    st.stop()

st.title("🛡️ SOVEREIGN DEFENSIVE CORE")

stats = main.get_system_stats()
col1, col2 = st.columns(2)
col1.metric("System Stability", f"{stats['stability']:.2%}")
col2.metric("Total Events", stats['total_events'])

with st.form("audit_form", clear_on_submit=True):
    prompt = st.text_input("Input Command...")
    submitted = st.form_submit_button("Execute Audit")

if submitted and prompt:
    with st.spinner("Executing..."):
        res = main.sovereign_agent_loop(prompt)
        if res.get("status") == "LOCKDOWN":
            st.error("!!! DEFENSIVE LOCKDOWN: RISK > 0.8 !!!")
        else:
            st.success(f"Audit Secure | Anchor: {res.get('ledger_hash', 'N/A')[:12]}")

st.subheader("⛓️ Defensive Ledger Stream")
for e in reversed(main.get_ledger_data()[-3:]):
    with st.expander(f"Anchor: {e.get('hash', '')[:8]}..."):
        st.write(f"**Intent**: {e.get('intent', 'N/A')}")
        st.write(f"**Critique**: {e.get('critique', 'N/A')}")
