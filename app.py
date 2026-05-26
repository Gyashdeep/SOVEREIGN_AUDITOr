import streamlit as st
from main import sovereign_agent_loop

# --- Aesthetic & UI Config ---
st.set_page_config(page_title="Sovereign Governance", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');
    html, body, .stApp { font-family: 'JetBrains Mono', monospace; background-color: #000000; color: #00FF41; }
    .status-box { border: 2px solid #00FF41; padding: 20px; background-color: #0a0a0a; text-align: center; margin-bottom: 20px; }
    .stChatMessage { background-color: #050505; border: 1px solid #333; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="status-box"><h2>🛡️ Sovereign Governance Interface</h2><p>✅ Ledger Integrity: ONLINE</p></div>', unsafe_allow_html=True)

# --- Session Management ---
if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message("assistant", avatar="⚡"): st.markdown(msg)

# --- Execution ---
if prompt := st.chat_input("Input Protocol..."):
    with st.chat_message("user", avatar="👤"): st.markdown(prompt)
    
    with st.spinner("Executing Sovereign Audit..."):
        result = sovereign_agent_loop(prompt)
        
        if result["status"] == "SHUTDOWN":
            output = f"⚠️ **CRITICAL HALT**: {result['msg']}"
        else:
            data = result['data']
            output = f"**Status**: {result['status']}\n\n**Risk Score**: {data['risk_score']}\n**Justification**: {data['justification']}\n\n---\n**Anchor**: `{result['ledger_hash']}`"
            
    st.session_state.messages.append(output)
    with st.chat_message("assistant", avatar="⚡"): st.markdown(output)
