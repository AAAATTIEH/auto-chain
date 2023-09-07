import streamlit as st
from firebase.service import load,save,load_all
import pandas as pd
import json
from utils.conversation_chain import get_conversation_chain

def save_model():
    
    name = st.text_input("Name",st.session_state.model["name"])
    
    #print(st.session_state.model["df"])
    df = st.session_state.model["df"]
    if(len(df) == 0):
        df = [{"issue":"Description Here","status":False}]
    df =  pd.DataFrame(df) 
    edited_df = st.data_editor(
        df,
        column_config={
            "issue": "Issue",
            
            "status": "Status",
        },
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,

    )
    if st.button("Save",use_container_width=True):
        if not name:
            st.error('Please provide a name')
            return
        with st.spinner("Saving"):
            save(st.session_state.model["id"],name,edited_df.to_dict(orient='records'),st.session_state.conversation_chain)
            st.success('Model Saved')
def load_model():
    with st.spinner("Loading Models"):
        names = load_all()
    col1, col2 = st.columns(2)
    if len(names) != 0:
        with col1:
            option = st.selectbox(
                        "Select your model",
                        options= names,
                        format_func=lambda x: str(x["name"]),
                        placeholder="Select Your Model",
                        label_visibility="collapsed"
                        
            )
        with col2:
            if st.button('Load Model',use_container_width=True):
                with st.spinner("Loading Model"):
                    load(option["id"])
                    st.session_state.model = option
                    st.session_state.data_type = "process"
                    get_conversation_chain(option["conversation"])
                    st.session_state.processed = True
                    st.experimental_rerun()