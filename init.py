from dotenv import load_dotenv
load_dotenv()
import streamlit as st

from utils.session_state import *
from utils.helpers import *
from streamlit.components.v1 import html
from custom_streamlit.components import *
from custom_streamlit.functions import *



def main():
  
    model_id = st.experimental_get_query_params().get('model_id', [''])[0]
    
    st.set_page_config(page_title="Auto Chain",
                       page_icon=":exploding_head:")
    
    with open('html/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)
   
    init_session_state()
    

    if(st.session_state.max_iterations!=0):

        
        executor_session_state().max_iterations = st.session_state.max_iterations
        st.session_state.max_iterations = 0
        

    
    func_handle_url(model_id)
    
    header,subheader = st.empty(),st.empty()

    if not st.session_state.processed:

        remove_dir('dataset/process/output')
        remove_dir('dataset/process/input')
        ##Custom Streamlit Header
        st_header_home(header,subheader)
        
        ## Custom Streamlit Process Button Block
        st_process()

        ## Custom Streamlit Sidebar Chat Models
        st_models_load()
        
        ## Custom Streamlit Changelog
        st_examples()
        st_changelog()

    else:
        
        
        # Custom Streamlit Sidebar Component        
        option = st_sidebar()

        # Custom Streamlit Chat Header Component           
        st_header_chat(header,option)

        # Custom Streamlit Chat Component        
        st_chat()

        # Custom Streamlit Model Save
        st_model_save()

        # Custom Streamlit Chat Input
        st_chat_input()
    
    
    with open('html/script.txt',"r") as f:
       js_content = f.read()
    
    html(f"""{js_content}""")
    

if __name__ == '__main__':
    main()



#"show in a histogram sbp as a function of age with 10 years bins"

