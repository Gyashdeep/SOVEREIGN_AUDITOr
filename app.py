import streamlit as st
import os
from auditor import sovereign_agent_loop

st.title("🛡️ Sovereign Auditor")

if "pending" not in st.session_state: st.session_state.pending = None

prompt = st.chat_input("Enter command...")
if prompt:
    res = sovereign_agent_loop(prompt)
    if res["status"] == "PENDING":
        st.session_state.pending = prompt
        st.warning(f"High risk: {res['data']['justification']}")
        if st.button("Authorize"):
            sovereign_agent_loop(st.session_state.pending, approved=True)
            st.success("Signed & Logged.")
    else:
        st.write("Action Authorized.")
