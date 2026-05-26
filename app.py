import streamlit as st
import os
from main import sovereign_agent_loop

# 1. Page Configuration
st.set_page_config(
    page_title="Sovereign Governance", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Cyberpunk/Terminal CSS Injection
hide_st_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'JetBrains Mono', monospace;
        background-color: #000000;
        color: #00FF41;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .status-box {
        border: 2px solid #00FF41;
        padding: 20px;
        background-color: #0a0a0a;
        text-align: center;
        margin-bottom: 20px;
        color: #00FF41;
    }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# 3. Interface Status
st.markdown("""
    <div class="status-box">
        <h2>🛡️ Sovereign Governance Interface</h2>
        <p>✅ Action Authorized & Ledger Anchored.</p>
    </div>
""", unsafe_allow_html=True)

# 4. Secure initialization check
if "GROQ_API_KEY" not in st.secrets and "GROQ_API_KEY" not in os.environ:
    st.error("SYSTEM ERROR: API Credentials Not Found.")
    st.stop()

# 5. Chatbox Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for message in st.session_state.messages:
    with st.chat_message("assistant", avatar="⚡"):
        st.markdown(message)

# Handle input
if prompt := st.chat_input("Command Input..."):
    st.session_state.messages.append(prompt)
    with st.chat_message("assistant", avatar="⚡"):
        st.markdown(prompt)
        
        # Here you would call your agent:
        # response = sovereign_agent_loop(prompt)
        # st.markdown(response)
