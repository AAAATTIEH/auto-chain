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
from firebase.service import load
from streamlit.components.v1 import html
load_dotenv()


import json
def stop_generating():
    max_iterations = executor_session_state().max_iterations
    executor_session_state().max_iterations = 0
    #executor_session_state().max_iterations = max_iterations
    st.session_state['executing'] = 'Forced'
    st.session_state.max_iterations = max_iterations
    st.experimental_rerun()
    
    
def reset_messages():
    try:
        messages_session_state().clear()
        executor_session_state().memory.clear() 
    except:
        print('No Memory for agent')

def delete_messages(index):
    print(f"Deleting Messages {index}")
    try:
        messages_session_state()[:] = messages_session_state()[:index]
        
        memory = executor_session_state().memory
        messages = memory.chat_memory.messages
        #Find index in memory
        memory_index = 0
        for i,message in enumerate(messages):
            class_name = message.__class__.__name__
            if(class_name == 'HumanMessage'):
                if(index == 0):
                    break
                memory_index = i
                index = index - 1
                
            
        messages[:] = messages[:memory_index]

        print(executor_session_state().memory)
        #messages_session_state().pop()
        #messages = messages_session_state()
        #print(len(messages))
        #messages = messages_session_state()[:index]
        #print(len(messages))
        #st.write(messages_session_state())
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



def execute(user_question):

    message_placeholder = st.container()

    executor_session_state()({
            "input":user_question
    },callbacks = [CustomHandler(message_placeholder = message_placeholder)])
    
    return 



def handle_userinput(user_question):

    if st.session_state['executing']==True or st.session_state['executing'] == 'Forced':
        st.session_state['executing']==False
        return
    with st.chat_message("user"):
        col1,col2 = st.columns([11,1])
        with col1:
            st.markdown(f'{user_question}',unsafe_allow_html=True)
        with col2:
            st.button('🗑',type="primary",on_click=delete_messages,args=(len(messages_session_state()),))

    messages_session_state().append({"role": "user", "content": user_question})
    messages_session_state().append({"role": "assistant", "content": "","disliked":False})
    
    with st.chat_message("assistant"):
        
        col1,col2,col3 = st.columns([1,1,1])
        empty = col2.empty()
        container = st.container()
        with col2:
            empty.button('Stop Generating',type="primary",key=f"c{len(messages_session_state())}",on_click=stop_generating)
                
        
        with container:
            try:
                st.session_state['executing'] = True
                execute(user_question = user_question)
                #print(executor_session_state().memory.chat_memory.messages)
                st.session_state['executing'] = False
            except:
                print(executor_session_state().memory.chat_memory.messages)
                st.session_state['executing'] = False
                print('AN ERROR HAPPENED')
                
        with col2:
            empty.empty()
        
    if "source_documents" in messages_session_state()[-1]:
        display_buttons_in_columns(3,messages_session_state()[-1]["source_documents"])
    st.session_state['executing'] = False

    
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
            docs = parse_image(file)
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
    
    model_id = st.experimental_get_query_params().get('model_id', [''])[0]
    st.set_page_config(page_title="Chat with Anything",
                       page_icon=":exploding_head:")
    
    with open('style/custom.css') as f:
        st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)
   
    init_session_state()
    if(st.session_state.max_iterations!=0):
        executor_session_state().max_iterations = st.session_state.max_iterations
        st.session_state.max_iterations = 0
    if(st.session_state.executing == 'Forced'):
        st.session_state.executing = False
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

            
            
    
       
    header = st.empty()
    subheader = st.empty()
    upload_docs = st.empty()
    if not st.session_state.processed:
        with header:
            annotated_text(
                    annotation(f"Chat with Anything",background="transparent",fontSize="40px",fontWeight="bold"),
                    annotation("pre-alpha", "v0.0.2",background="#afa",fontSize="18px"),
            ) 
        remove_dir('dataset/process/output')
        #remove_dir('dataset/process')
        with subheader:
            st.subheader("Your documents")
        upload_docs = st.file_uploader(
            "Upload your Documents here and click on 'Process'", accept_multiple_files=True,type=["txt","pdf","png","mp3","docx","csv","jpg"])
        process_button = st.button("Process",use_container_width=True,type='primary')
        
       
    
        if process_button:
            my_bar = st.progress(0, text="Operation in progress")
            with my_bar:
                process(upload_docs)
                c = get_conversation_chain()
                if (c):
                    st.session_state.processed = True
                    st.session_state.model = {
                        'id':'NEW',
                        'index':0,
                        'name':''
                    }
                    st.experimental_rerun()
                else:
                    st.error('No Agents Avaialable')
        #st.session_state["model"] = {
        #        "name":"",
        #        "id":"NEW",
        #        "index":0,
        #        "df":[]
        #    }
        load_model()
    
        with st.expander("## ChangeLog"):
            st.markdown(changelog_markdown,unsafe_allow_html=True)
    else:
        
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
                on_change=agent_changed,
            )
            
            if option:
                eval(agents_classes[option]["annotated"])
                if(st.session_state.agent != option):
                    change_agent_session_state(option)
            
            with header:
                col1,col2 = st.columns([11,1])
                with col1:
                    annotated_text(
                        annotation(f"""{option}""",background="transparent",fontSize="28px",fontWeight="bold"),
                    ) 
                with col2:
                    st.button('💡',type="primary",use_container_width=True,on_click=reset_messages)
                
                
                
                
        for i,message in enumerate(messages_session_state()):
            with st.chat_message(message["role"]):
                
                col1,col2 = st.columns([11,1])
                with col1:
                    placeholder = st.container()
                    st_multi_modal(placeholder,message["content"],[])
                with col2:
                    if(message["role"] == "user"):
                        st.button('🗑',type="primary",key=f"b{i}",on_click=delete_messages,args=(i,))
                    else:
                        dislike = st.empty()
                        report = st.empty()
                        
                        if(not message['disliked']):
                            if dislike.button('👎',key=f"d{i}"):
                                dislike.button('👎',type='primary',key=f"d{i}-active")
                                messages_session_state()[i]['disliked'] = True
                                
                        else:
                            
                            if dislike.button('👎',key=f"d{i}-active",type='primary'):
                                dislike.button('👎',key=f"d{i}")
                                messages_session_state()[i]['disliked'] = False
                            
                           
                
                if "source_documents" in message:
                    display_buttons_in_columns(3,message["source_documents"])
        if st.session_state['executing'] == 'Forced':
            disabled = False
        else:
            disabled = st.session_state['executing']
        
        user_question = st.chat_input("Ask a question about your documents:",disabled=disabled,key='chat-enabled')    
        
        with st.sidebar:
            save_model()
        if user_question:
            st.chat_input("Ask a question about your documents:",disabled=True,key='chat-disabled') 
            handle_userinput(user_question)
            
            st.experimental_rerun()
        
    #button = """<a href="/?name=John" target="_self" onclick="func"><button>Test Link</button></a>"""
    #st.markdown(f"This is a button {button}", unsafe_allow_html=True)
    # Display a button using HTML
    
    # Add some JavaScript code to capture button presses
    my_html = """

        <script>
            
            let doc = window.parent.document
            doc.querySelector("iframe").style.display = 'none'

            const parentElement = doc.querySelector(".main");

            parentElement.addEventListener("click", function(event) {
            
            if (event.target.innerText=='👎') {
                
                let message = event.target.closest(".stChatMessage")
                console.log(message.style.backgroundColor)
                if(message.style.backgroundColor == 'rgba(255, 75, 75, 0.4)')
                    message.style.backgroundColor = 'white'
                else if(message.style.backgroundColor == 'white')
                    message.style.backgroundColor = 'rgba(255, 75, 75, 0.4)'
                else
                    message.style.backgroundColor = 'rgba(255, 75, 75, 0.4)'
                console.log(message.style.backgroundColor)
            }
            });
            
            let messages = doc.querySelectorAll(".stChatMessage")
            for (var i=0;i<messages.length;i++){
                    message = messages[i]
                    console.log(message.querySelector('[kind="primary"]'))
                    if(i%2!=0){
                        primary = message.querySelector('[kind="primary"]')
                        secondary = message.querySelector('[kind="secondary"]')
                        if(primary && primary.innerText == '👎')
                            message.style.backgroundColor = 'rgba(255, 75, 75, 0.4)'
                        else if(secondary && secondary.innerText == '👎')
                            message.style.backgroundColor = 'white'
                    }
                
            }
            console.log(messages)
            
            
            
            
        </script>
        """
    html(my_html)

if __name__ == '__main__':
    main()



#"show in a histogram sbp as a function of age with 10 years bins"

