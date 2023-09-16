import streamlit as st
from utils.session_state import *
from custom_streamlit.functions import func_delete_messages,func_stop_generating,func_sources_buttons
from models.execute import execute
def func_handle_chat_input(user_question):
    if st.session_state['executing']==True or st.session_state['executing'] == 'Forced':
        st.session_state['executing']==False
        return
    with st.chat_message("user"):
        col1,col2 = st.columns([11,1])
        with col1:
            st.markdown(f'{user_question}',unsafe_allow_html=True)
        with col2:
            st.button('🗑',type="primary",on_click=func_delete_messages,args=(len(messages_session_state()),))

    messages_session_state().append({"role": "user", "content": user_question})
    messages_session_state().append({"role": "assistant", "content": "","disliked":False})
    
    with st.chat_message("assistant"):
        
        col1,col2,col3 = st.columns([1,1,1])
        empty = col2.empty()
        container = st.container()
        with col2:
            empty.button('Stop Generating',type="primary",key=f"c{len(messages_session_state())}",on_click=func_stop_generating)
                
        
        with container:
            try:
                #st.session_state['executing'] = True
                execute(user_question = user_question)
              
                #st.session_state['executing'] = False
            except Exception as e:
                # Handle the exception and print the error message
                print("An error occurred:", e)
                st.session_state['executing'] = False
                
                
        with col2:
            empty.empty()
        
    if "source_documents" in messages_session_state()[-1]:
        func_sources_buttons(3,messages_session_state()[-1]["source_documents"])
    st.session_state['executing'] = False

