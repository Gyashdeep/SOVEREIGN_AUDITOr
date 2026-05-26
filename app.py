import streamlit as st
from main import sovereign_agent_loop, get_ledger_state

st.set_page_config(page_title="Sovereign Governance", layout="wide")

# Extreme Terminal Styling
st.markdown("""<style>
    .stApp { background-color: #000; color: #00FF41; font-family: 'JetBrains Mono'; }
    .hash-link { font-size: 0.8em; color: #888; border-left: 2px solid #00FF41; padding-left: 10px; }
</style>""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 🛡️ Sovereign Governance Core")
    if prompt := st.chat_input("Command Input..."):
        res = sovereign_agent_loop(prompt)
        st.write(f"**Result**: {res['status']} | **Hash**: `{res.get('ledger_hash', 'N/A')}`")

with col2:
    st.markdown("### ⛓️ Ledger Anchor Stream")
    ledger = get_ledger_state()
    for entry in reversed(ledger[-5:]):
        st.markdown(f"<div class='hash-link'>Block: {entry['hash'][:10]}...<br>Risk: {entry['decision']['risk_score']}</div>", unsafe_allow_html=True)
