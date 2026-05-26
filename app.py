import streamlit as st
from main import sovereign_agent_loop

st.set_page_config(page_title="Sovereign Governance", layout="centered")

st.markdown("""<style>
    .stApp { background-color: #000; color: #00FF41; font-family: 'Courier New', monospace; }
    .status-box { border: 2px solid #00FF41; padding: 15px; text-align: center; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="status-box"><h2>🛡️ Sovereign Governance Interface</h2></div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message("assistant", avatar="⚡"):
        st.markdown(msg)

if prompt := st.chat_input("Command Input..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    with st.spinner("Processing..."):
        try:
            res = sovereign_agent_loop(prompt)
            if res["status"] == "SHUTDOWN":
                output = f"⚠️ **{res['msg']}**"
            else:
                output = f"**Status**: {res['status']}\n**Justification**: {res['data']['justification']}\n**Hash**: `{res['ledger_hash']}`"
            
            st.session_state.messages.append(output)
            with st.chat_message("assistant", avatar="⚡"):
                st.markdown(output)
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
