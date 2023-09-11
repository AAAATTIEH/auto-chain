name = "Agent 3: BLIP Image Agent"
arguments = ["images"]
annotated = ["ZeroShot Agent","Default LLM","Path, Caption, Detection Tool"]

from langchain.tools import BaseTool

from models.tools.image_caption import ImageCaptionTool
from models.tools.image_path_finder import ImagePathFinderTool
from models.tools.object_detection import ObjectDetectionTool
from langchain.agents import initialize_agent

from langchain.chains.conversation.memory import ConversationBufferWindowMemory

from models.llms.llms import *


def agent(images):
    tools = [ImagePathFinderTool(paths=images),ImageCaptionTool(),ObjectDetectionTool()]

    conversational_memory = ConversationBufferWindowMemory(
        memory_key='chat_history',
        k=5,
        return_messages=True
    )


    
    agent = initialize_agent(
        agent="zero-shot-react-description",
        tools=tools,
        llm=llm,
        max_iterations=5,
        verbose=True,
        memory=conversational_memory,
        early_stopping_method='generate'
    )
 
    return agent
