import streamlit as st
from auditor import sovereign_agent_loop

st.set_page_config(page_title="🛡️Sovereign Auditor", layout="centered")
st.title("🛡️ Sovereign Governance Interface")

if "pending" not in st.session_state: st.session_state.pending = None

prompt = st.chat_input("Command the Sovereign Auditor...")
if prompt:
    res = sovereign_agent_loop(prompt)
    if res["status"] == "PENDING":
        st.session_state.pending = prompt
        st.warning(f"Governance Hold: Risk Score {res['data']['risk_score']}")
        if st.button("EXECUTE GOVERNANCE AUTHORIZATION"):
            sovereign_agent_loop(st.session_state.pending, approved=True)
            st.success("Transaction Signed & Anchored to Ledger.")
    elif res["status"] == "SHUTDOWN":
        st.error(res["msg"])
    else:
        st.write("✅ Action Authorized & Ledger Anchored.")
