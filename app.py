import streamlit as st
from auditor import sovereign_agent_loop, get_last_hash

st.set_page_config(page_title="Sovereign Auditor", layout="wide")
st.title("🛡️ Sovereign Auditor Portal")

if "pending_intent" not in st.session_state:
    st.session_state.pending_intent = None

prompt = st.chat_input("Enter command...")

if prompt:
    result = sovereign_agent_loop(prompt)
    if result["status"] == "PENDING_APPROVAL":
        st.session_state.pending_intent = prompt
        st.warning(f"High risk detected: {result['data']['justification']}")
        if st.button("Authorize Action"):
            sovereign_agent_loop(st.session_state.pending_intent, approved=True)
            st.success("Action Authorized!")
    else:
        st.write(result["msg"] if "msg" in result else "Action Authorized.")

with st.sidebar:
    st.write("Ledger Head Hash:", get_last_hash()[:16] + "...")
