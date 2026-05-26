import streamlit as st
from main import sovereign_agent_loop, get_ledger_state

st.set_page_config(page_title="Sovereign Governance", layout="wide")

st.markdown("""<style>
    .stApp { background-color: #000; color: #00FF41; font-family: 'Courier New', monospace; }
    .status-box { border: 2px solid #00FF41; padding: 15px; text-align: center; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="status-box"><h2>🛡️ Sovereign Governance Core</h2></div>', unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages: st.chat_message("assistant", avatar="⚡").markdown(msg)

if prompt := st.chat_input("Command Input..."):
    with st.chat_message("user", avatar="👤"): st.markdown(prompt)
    
    with st.spinner("Anchoring to Ledger..."):
        try:
            res = sovereign_agent_loop(prompt)
            if res["status"] == "SHUTDOWN":
                output = f"⚠️ **CRITICAL HALT**: {res['msg']}"
            else:
                data = res['data']
                output = f"**Status**: {res['status']}\n**Risk**: {data['risk_score']}\n**Justification**: {data['justification']}\n**Anchor**: `{res['ledger_hash']}`"
            
            st.session_state.messages.append(output)
            st.chat_message("assistant", avatar="⚡").markdown(output)
        except Exception as e:
            st.error(f"SYSTEM ERROR: {e}")

# Visualizing the chain logic
