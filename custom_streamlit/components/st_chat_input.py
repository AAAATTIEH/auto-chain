import streamlit as st
from custom_streamlit.functions import func_handle_chat_input
def st_chat_input():
        if st.session_state['executing'] == 'Forced':
            disabled = False
        else:
            disabled = st.session_state['executing']
        user_question = st.chat_input("Ask a question about your documents:",disabled=disabled,key='chat-enabled')    
        if user_question:
            st.chat_input("Ask a question about your documents:",disabled=True,key='chat-disabled') 
            func_handle_chat_input(user_question)
            
            st.experimental_rerun()