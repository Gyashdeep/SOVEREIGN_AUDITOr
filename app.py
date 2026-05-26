import streamlit as st
import os
from auditor import sovereign_agent_loop, verify_ledger

st.set_page_config(page_title="Sovereign Auditor Portal", layout="wide")
st.title("🛡️ Sovereign Auditor Portal")

with st.sidebar:
    st.header("Security Controls")
    if st.button("Audit Integrity Scan"):
        secret = os.environ.get("AUDIT_SECRET_KEY", "prod-hardened-key-12345").encode()
        if verify_ledger("sovereign_evidence_ledger.log", secret):
            st.success("Chain Validated: System Secure.")
        else:
            st.error("INTEGRITY BREACH: Log tampered!")

if "pending" not in st.session_state: st.session_state.pending = None

prompt = st.chat_input("Command the auditor...")
if prompt:
    res = sovereign_agent_loop(prompt)
    if res["status"] == "PENDING_APPROVAL":
        st.session_state.pending = prompt
        st.warning(f"HIGH RISK: {res['data']['justification']}")
        if st.button("Authorize Action"):
            sovereign_agent_loop(st.session_state.pending, approved=True)
            st.success("Authorization Sealed.")
    elif res["status"] == "SHUTDOWN":
        st.error(res["msg"])
    else:
        st.write("Action Authorized.")
