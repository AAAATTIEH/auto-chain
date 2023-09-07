import streamlit as st

import pandas as pd
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from annotated_text import annotated_text,annotation
from utils.changelog import changelog_markdown
from utils.session_state import *
from utils.docs_parse import *
from utils.callback import CustomHandler
from utils.helpers import *
from models.agents import agents_classes
from utils.multi_modal import st_multi_modal
from utils.conversation_chain import get_conversation_chain
from components.load_model import load_model,save_model
load_dotenv()


import json

def delete_messages():
    try:
        messages_session_state().clear()
        executor_session_state().memory.clear() 
    except:
        print('No Memory for agent')
def get_vectorstore(documents):
    embeddings = OpenAIEmbeddings()
    text_splitter = CharacterTextSplitter(
        chunk_size =1000,
        chunk_overlap = 0,
        separator= "\n"
    )
    
    docs = text_splitter.split_documents(documents=documents)
    if(len(docs) == 0):
        return False
    else:
        for idx, doc in enumerate(docs, start=1):
            doc.metadata['doc_id'] = idx
            doc.metadata['source'] = doc.metadata['source'].split("\\")[-1]
        vectorstore = FAISS.from_documents(documents=docs, embedding=embeddings)
        return vectorstore



def visualize(user_question):

    message_placeholder = st.container()
    return executor_session_state()({
        "input":user_question
    },callbacks = [CustomHandler(message_placeholder = message_placeholder)])



def handle_userinput(user_question):

    with st.chat_message("user"):
        st.markdown(user_question)
    messages_session_state().append({"role": "user", "content": user_question})
    messages_session_state().append({"role": "assistant", "content": ""})

    with st.chat_message("assistant"):
        visualize(user_question = user_question)
    if "source_documents" in messages_session_state()[-1]:
        display_buttons_in_columns(3,messages_session_state()[-1]["source_documents"])

    
    
def process(files):
    documents = []
    remove_dir('dataset/process')
    os.makedirs('dataset/process/input/tables')
    os.makedirs('dataset/process/input/images')
    os.makedirs('dataset/process/input/vector')
    os.makedirs('dataset/process/output/tables')
    os.makedirs('dataset/process/output/images')
    os.makedirs('dataset/process/output/vector')
    #images_metadata = {}

    for i,file in enumerate(files):
        st.progress((i)/len(files), text=f'Processing {file.name}')
        if file.name.endswith('.pdf'):
            docs = parse_pdf(file)
            documents.extend(docs)
        elif file.name.endswith('.csv'):
            parse_csv(file)
        elif file.name.endswith('.pptx'):
            docs = parse_pptx(file)
            documents.extend(docs)
        elif file.name.endswith('.links.txt'):
            docs = parse_links(file)
            documents.extend(docs)
        elif file.name.endswith('.txt'):
            docs = parse_txt(file)
            documents.extend(docs)
        elif file.name.endswith('.docx'):
            docs = parse_docx(file)
            documents.extend(docs)
        elif file.name.endswith('.png') or file.name.endswith('.jpg') or file.name.endswith('.jpeg'):
            print(file)
            docs = parse_image(file)
            print(docs)
            documents.extend(docs)
            #file_path,metadata = parse_image(file)
            #images_metadata[file_path] = metadata
        elif file.name.endswith('.mp3'):
            docs = parse_audio(file)
            documents.extend(docs)
        st.session_state.files.append(file.name)
    #with open('dataset/process/images/metadata.json', "w") as json_file:
    #    json.dump(images_metadata, json_file, indent=4)
    remove_dir('temp')

    # create vector store
    vectorstore = get_vectorstore(documents)
    

    if(vectorstore):
        vectorstore.save_local("dataset/process/input/vector")
   
def show_source(source,documents):
    with st.sidebar:
        st.subheader(f"Source: {source}")
        for doc in documents:
            st.write(f"...{doc.page_content}...")
            st.write('----')

count = 0 
def display_buttons_in_columns(num_columns, values):
    global count

    # Calculate the number of rows needed to display the values
    num_rows = -(-len(values) // num_columns)  # Ceiling division
    sources = list(values.keys())

    # Create a grid layout with the specified number of columns
    col_width = 12 // num_columns
    for row in range(num_rows):
        cols = st.columns(num_columns)
        for col_idx, col in enumerate(cols):
            value_idx = row * num_columns + col_idx
            if value_idx < len(values):
                source = sources[value_idx]
                count = count+1
                col.button(source,key=f'b{count}',use_container_width=True,on_click=show_source,args=(source,values[source],))
def agent_changed():
    st.session_state.agent_changed = True


def main():
    #name = st.experimental_get_query_params().get('name', [''])[0]
    st.set_page_config(page_title="Chat with Anything",
                       page_icon=":exploding_head:")
    
    with open('style/custom.css') as f:
        st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)
   
    init_session_state()
    
    subheader = st.empty()
    place = st.empty()
    
    with place:
        annotated_text(
                annotation(f"Chat with Anything",background="transparent",fontSize="40px",fontWeight="bold"),
                annotation("pre-alpha", "v0.0.2",background="#afa",fontSize="18px"),
        )    
    
    if not st.session_state.processed:
        remove_dir('dataset/process/output')
        #remove_dir('dataset/process')
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your Documents here and click on 'Process'", accept_multiple_files=True,type=["txt","pdf","png","mp3","docx","csv","jpg"])
        process_button = st.button("Process",use_container_width=True,type='primary')
        
       
        
        if process_button:
            my_bar = st.progress(0, text="Operation in progress")
            with my_bar:
                process(pdf_docs)
                st.session_state.data_type  = "process"
                c = get_conversation_chain()
                if (c):
                    st.session_state.processed = True
                    st.experimental_rerun()
                else:
                    st.session_state.data_type  = None
                    st.error('No Agents Avaialable')
        #st.session_state["model"] = {
        #        "name":"",
        #        "id":"NEW",
        #        "index":0,
        #        "df":[]
        #    }
        load_model()
    
        with st.expander("## ChangeLog"):
            st.markdown(changelog_markdown)
    else:
        
        with st.sidebar:
            if st.button('Retry',type="primary",use_container_width=True):
                reset_session_state()
            
            with st.expander("Uploaded Files"):
                st.write(', '.join(st.session_state.files))
            option = st.selectbox(
                "Select an Agent",
                st.session_state.conversation_chain.keys(),
                placeholder="Select Your Agent",
                on_change=agent_changed,
            )
            
            if option:
                eval(agents_classes[option]["annotated"])
                if(st.session_state.agent != option):
                    change_agent_session_state(option)
            save_model()
            with place:
                col1,col2 = st.columns([11,1])
                with col1:
                    annotated_text(
                        annotation(f"""{option}""",background="transparent",fontSize="28px",fontWeight="bold"),
                    ) 
                with col2:
                    st.button('↺',type="primary",use_container_width=True,on_click=delete_messages)
            with subheader:
                    pass
                    
                
                
                
        for message in messages_session_state():
            with st.chat_message(message["role"]):
                placeholder = st.container()
                st_multi_modal(placeholder,message["content"],[])
                
                if "source_documents" in message:
                    display_buttons_in_columns(3,message["source_documents"])                     
        
        user_question = st.chat_input("Ask a question about your documents:")
        
        if user_question:
            handle_userinput(user_question)
    #button = """<a href="/?name=John" target="_self" onclick="func"><button>Test Link</button></a>"""
    #st.markdown(f"This is a button {button}", unsafe_allow_html=True)
    
if __name__ == '__main__':
    main()



#"show in a histogram sbp as a function of age with 10 years bins"