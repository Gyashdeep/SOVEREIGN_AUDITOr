import streamlit as st
from main import sovereign_agent_loop, get_ledger_data, get_system_stats, verify_ledger

st.set_page_config(page_title="Sovereign Governance", layout="wide")
st.markdown("""<style>.stApp { background-color: #050505; color: #00FF41; font-family: 'Courier New'; }</style>""", unsafe_allow_html=True)

if not verify_ledger():
    st.error("!!! FATAL: LEDGER INTEGRITY BREACHED !!!")
    st.stop()

st.title("🛡️ SOVEREIGN DEFENSIVE CORE")

# Metrics Display
stats = get_system_stats()
col1, col2 = st.columns(2)
col1.metric("System Stability", f"{stats['stability']:.2%}")
col2.metric("Total Events", stats['total_events'])

# Processing
if prompt := st.chat_input("Input Command..."):
    with st.spinner("Executing Multi-Agent Audit..."):
        res = sovereign_agent_loop(prompt)
        if res["status"] == "LOCKDOWN": st.error("!!! DEFENSIVE LOCKDOWN !!!")
        else: st.success(f"Audit Secure | Anchor: {res['ledger_hash'][:12]}")

# Ledger View
st.subheader("⛓️ Defensive Ledger Stream")
for e in reversed(get_ledger_data()[-3:]):
    with st.expander(f"Anchor: {e['hash'][:8]}..."):
        st.write(f"**Intent**: {e['intent']}")
        st.write(f"**Critique**: {e['critique']}")
