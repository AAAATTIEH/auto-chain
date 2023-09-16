import streamlit as st
from utils.session_state import load_session_state
from utils.conversation_chain import get_conversation_chain
from firebase.service import load
def func_handle_url(model_id):
    if(model_id and model_id!='chat' and not st.session_state.processed ):
        my_bar = st.progress(0, text="Operation in progress")
        with my_bar:
            model,agents = load(model_id)
            if(model == None or agents == None):
                st.error('Chat Model Does Not Exist')
                st.experimental_set_query_params()
            else:
                st.session_state.model = model
                get_conversation_chain(agents["conversation"])
                st.session_state.processed = True
                load_session_state()
                st.experimental_rerun()
        
    if(model_id == 'chat' and not st.session_state.processed):
        my_bar = st.progress(0, text="Operation in progress")
        with my_bar:
            
            get_conversation_chain()
            st.session_state.processed = True
            st.session_state.model = {
                        'id':'NEW',
                        'index':0,
                        'name':''
            }
            st.experimental_rerun()