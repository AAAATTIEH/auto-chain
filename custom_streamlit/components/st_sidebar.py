import streamlit as st
from custom_streamlit.functions import func_agent_changed
from utils.session_state import change_agent_session_state
from models.agents import agents_classes
from annotated_text import annotated_text,annotation
def st_sidebar():
    with st.sidebar:
        col1,col2 = st.columns(2)
        with col1:
            st.markdown(""" <a href="/" target="_self" style="color:rgb(49, 51, 63)"><button class="secondary-button">Retry</button></a>""",unsafe_allow_html=True)
            
        with col2:
            st.markdown(' <a href="/?model_id=chat" target="_self" style="color:rgb(49, 51, 63)"><button class="primary-button">New Chat</button></a>',unsafe_allow_html=True)
        
        option = st.selectbox(
            "Select an Agent",
            st.session_state.conversation_chain.keys(),
            placeholder="Select Your Agent",
            on_change=func_agent_changed,
        )
        
        if option:
            eval(agents_classes[option]["annotated"])
            if(st.session_state.agent != option):
                change_agent_session_state(option)
        return option