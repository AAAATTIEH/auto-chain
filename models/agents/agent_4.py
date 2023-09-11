name = "Agent 4: Chooch Image Agent"
arguments = ["images"]
annotated = ["ZeroShot Agent","Default LLM","Path, Chooch Tool"]


from langchain.tools import BaseTool

from models.tools.chooch_chat import ChoochChatTool
from models.tools.image_path_finder import ImagePathFinderTool
from models.tools.object_detection import ObjectDetectionTool
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import (
    AgentTokenBufferMemory,
)

from langchain.agents import AgentType


from models.llms.llms import *
def agent(images):

    tools = [ImagePathFinderTool(paths = images),ChoochChatTool()]

    conversational_memory = ConversationBufferWindowMemory(
        memory_key='chat_history',
        k=5,
        return_messages=True
    )
    


    token_memory = AgentTokenBufferMemory(
            memory_key='chat_history', llm=llm,return_messages=True
    )
    agent = initialize_agent(
        #agent="zero-shot-react-description",
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        tools=tools,
        llm=llm,
        max_iterations=5,
        memory=conversational_memory,
        early_stopping_method='generate',
        #return_intermediate_steps = True
    )

    return agent
