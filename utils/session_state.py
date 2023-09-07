import streamlit as st
def init_session_state():
    if "data_type" not in st.session_state:
        st.session_state.data_type  = None
    if "files" not in st.session_state:
        st.session_state.files = []
    if "model" not in st.session_state:
        st.session_state.model = {}    
    if "conversation_chain" not in st.session_state:
        st.session_state.conversation_chain = {}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "processed" not in st.session_state:
        st.session_state.processed = False
    if "agent_changed" not in st.session_state:
        st.session_state.agent_changed  = True
    if "agent" not in st.session_state:
        st.session_state.agent  = None
def reset_session_state():
    st.session_state.files = []
    st.session_state.chat_history = None
    st.session_state.conversation_chain = {}
    st.session_state.model = {}
    st.session_state.data_type = None
    st.session_state.agent = None
    st.session_state.processed  = False
    st.session_state.agent_changed  = True
    st.session_state.data_type  = None
    st.experimental_rerun()

def change_agent_session_state(option):
    st.session_state.agent = option
    st.session_state.chat_history = None
    st.session_state.agent_changed = False

def messages_session_state():
    return st.session_state.conversation_chain[st.session_state.agent]["messages"]
def executor_session_state():
    return st.session_state.conversation_chain[st.session_state.agent]["executor"]