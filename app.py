import streamlit as st
from auditor import sovereign_agent_loop, verify_ledger

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Sovereign Auditor Portal", layout="wide")
st.title("🛡️ Sovereign Auditor v4.0")
st.markdown("Cryptographically verified, compliance-bound AI infrastructure.")

# --- SIDEBAR: COMPLIANCE & INTEGRITY ---
with st.sidebar:
    st.header("Security Controls")
    st.markdown("Manage system integrity and audit logs.")
    
    if st.button("Audit Ledger Integrity"):
        with st.status("Verifying cryptographic chain...", expanded=True) as status:
            # st.secrets is used for production; fallback to env var for local dev
            secret = st.secrets.get("AUDIT_SECRET_KEY") or os.environ.get("AUDIT_SECRET_KEY")
            
            is_valid = verify_ledger("sovereign_evidence_ledger.log", secret.encode())
            
            if is_valid:
                status.update(label="Chain Validated", state="complete")
                st.success("Ledger Integrity Confirmed.")
            else:
                status.update(label="Integrity Breach!", state="error")
                st.error("TAMPERING DETECTED: Chain broken.")

# --- MAIN CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Loop
if prompt := st.chat_input("Enter audit instruction or system command..."):
    # Render user prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent Execution
    with st.chat_message("assistant"):
        with st.spinner("Analyzing risk and compliance..."):
            response = sovereign_agent_loop(prompt)
            
            # Handle HITL (Human-in-the-Loop) flow
            if response.get("status") == "PENDING_APPROVAL":
                st.warning(f"High risk detected: {response['data']['justification']}")
                if st.button("Authorize Action"):
                    final_res = sovereign_agent_loop(prompt, approved=True)
                    st.success("Action Authorized and Logged.")
                    st.session_state.messages.append({"role": "assistant", "content": "Action Authorized."})
            else:
                st.markdown(response.get("msg", "Action Processed."))
                st.session_state.messages.append({"role": "assistant", "content": response.get("msg", "Processed.")})
