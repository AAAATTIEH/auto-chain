import streamlit as st
from firebase.service import load,save,load_all,delete
import pandas as pd
import json
from utils.conversation_chain import get_conversation_chain
from utils.session_state import *
from custom_components import my_component
def save_df():
    #st.session_state.df_changed = True
    df = issues_session_state()
    if(len(df) == 0):
        df = [{"issue":"Description Here"}]
    dataframe = st.session_state[st.session_state.agent]

    #df = [{"issue":dataframe["edited_rows"][0]["issue"]}]
   
    for key,row in dataframe["edited_rows"].items():
        if "issue" in row:
            df[key]["issue"] = row["issue"]
    for row in dataframe["added_rows"]:
        if "issue" in row:
            df.append({"issue":row["issue"]})
    count = 0
    for row in dataframe["deleted_rows"]:
        df.pop(row-count)
        count +=1     
    issues_session_state()[:] = df

def save_model():
    container = st.container()
    name = st.text_input("Name",st.session_state.model["name"])
    
    #print(st.session_state.model["df"])
    df = issues_session_state()
    if(len(df) == 0):
        df = [{"issue":"Description Here"}]
    df =  pd.DataFrame(df) 
    if true_key_session_state('r-'):
        st.text_input('Hello')
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        column_config={
            "issue": "Issue"
        },
        num_rows="dynamic",
        hide_index=True,
        key=f'{st.session_state.agent}',
        on_change=save_df,
    )
    
    with container:
        unsaved = st.empty()
        if st.button("Save",use_container_width=True,type='primary'):
            if not name:
                st.error('Please provide a name')
                return
            my_bar = st.progress(0, text=f'Operation in Progress')
            with my_bar:
                show = False
                if 'show' in st.session_state:
                    show = st.session_state['show']
                id = save(st.session_state.model["id"],name,st.session_state.conversation_chain,show)
                load_session_state()
                st.success(f'Chat Model Saved ID {id}')
                st.experimental_set_query_params(model_id=id)
                st.session_state.model['id'] = id
        if st.session_state.model['id'] == "NEW":
            st.checkbox('Show',key='show',value=True)
           
        if(compare_session_state()):
            unsaved.error("**Unsaved Changes**")
            #unsaved.markdown('<span style="color:rgb(255, 75, 75);font-weight:bolder">*Unsaved Changes</span>',unsafe_allow_html=True)
         
def load_model():
    with st.sidebar:
        
            
        option = st.selectbox(
                    "Sort by",
                    options= [
                        {"name":"Last Updated","value":"last_updated"},
                        {"name":"Created","value":"created_at"},
                        {"name":"Issues","value":"total_issues"}
                        ],
                    format_func=lambda x: str(x["name"]),
                    placeholder="Sort by",
                    
                    
        )
        with st.spinner("Loading Models"):
            names = load_all(option["value"])
            if(len(names)!=0):
                num_clicks = my_component(names,type=option["value"],key='hg')
                if num_clicks:
                    if(num_clicks['type'] == 'delete'):

                        delete(num_clicks["id"])
                        st.experimental_rerun()
                        
                    else:
                        st.experimental_set_query_params(model_id=num_clicks['id'])
                        st.experimental_rerun()
            else:
                st.write(" No Chat Models Found")        