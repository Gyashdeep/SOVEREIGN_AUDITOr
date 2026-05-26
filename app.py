import streamlit as st
from main import sovereign_agent_loop, check_integrity

st.set_page_config(page_title="Sovereign Governance", layout="centered")

# UI Aesthetic
st.markdown("""<style>
    .stApp { background-color: #000; color: #00FF41; font-family: 'JetBrains Mono'; }
    .status-box { border: 2px solid #00FF41; padding: 15px; text-align: center; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="status-box"><h2>🛡️ Sovereign Governance</h2></div>', unsafe_allow_html=True)

# Integrity Check
if not check_integrity():
    st.error("!!! FATAL: LEDGER TAMPERING DETECTED !!!")
    st.stop()

if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages: st.chat_message("assistant", avatar="⚡").markdown(msg)

if prompt := st.chat_input("Command Input..."):
    with st.chat_message("user", avatar="👤"): st.markdown(prompt)
    
    with st.spinner("Anchoring to Ledger..."):
        res = sovereign_agent_loop(prompt)
        if res["status"] == "SHUTDOWN":
            output = f"⚠️ {res['msg']}"
        else:
            output = f"**Status**: {res['status']}\n**Justification**: {res['data']['justification']}\n**Hash**: `{res['ledger_hash']}`"
    
    st.session_state.messages.append(output)
    st.chat_message("assistant", avatar="⚡").markdown(output)
