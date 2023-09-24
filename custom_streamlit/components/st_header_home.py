import streamlit as st
from annotated_text import annotated_text,annotation
def st_header_home(header,subheader):
    with header:
            annotated_text(
                    annotation(f"Auto Chain",background="transparent",fontSize="40px",fontWeight="bold"),
                    annotation("pre-alpha", "v0.0.5",background="#f5f",fontSize="18px"),
            ) 
        
        #remove_dir('dataset/process')
    with subheader:
        st.subheader("Your documents")
        