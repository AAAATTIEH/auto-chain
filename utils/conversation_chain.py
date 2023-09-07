import streamlit as st
from langchain.embeddings import OpenAIEmbeddings

from langchain.vectorstores import FAISS
from models.agents import agents_classes
import json
from utils.helpers import get_file_names
def get_conversation_chain(conversation=None):
    st.progress(100, text=f'Getting Agents')
    datatype = st.session_state.data_type
    embeddings = OpenAIEmbeddings()
    try:
        vectorstore = FAISS.load_local(f"dataset/{datatype}/input/vector", embeddings)
    except:
        vectorstore = False
    try:
        csvs = get_file_names(f"dataset/{st.session_state.data_type}/input/tables")
    except:
        csvs = False
    try:
        images = json.loads(open(f'dataset/{st.session_state.data_type}/input/images/metadata.json', 'r').read())
    except:
        images = False
    conversation_chain = {}
    for el in agents_classes:
        arguments = agents_classes[el]['arguments']
        parameters = {}
        included = True
        for arg in arguments:
            value = eval(arg)
            if not value:
                included = False
                break
            parameters[arg] = eval(arg)
        if included:
            if(conversation):
                if(conversation[el]):
                    conversation_chain[el] = {
                        "executor":agents_classes[el]['func'](**parameters),
                        "messages":conversation[el]["messages"]
                    }
            else:
                conversation_chain[el] = {
                    "executor":agents_classes[el]['func'](**parameters),
                    "messages":[]
                }
    if len(conversation_chain) == 0:
        return False
    st.session_state['conversation_chain'] = conversation_chain

   
    return True