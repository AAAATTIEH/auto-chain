name = "🖼️ Chooch Image Agent"
arguments = ["images"]
annotated = ["ZeroShot Agent","Default LLM","Path, Chooch Tool"]


from langchain.tools import BaseTool
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
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
from models.memory.custom_image_memory import CustomImageMemory
from models.memory.custom_image_memory import CustomImageMemory
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain import OpenAI, LLMChain, PromptTemplate
import langchain 
langchain.debug = True
from models.llms.llms import *
"""def agent(images):

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
        memory=token_memory,
        early_stopping_method='generate',
        return_intermediate_steps = True
    )

    return agent
"""
def agent(images):
    tools = [ImagePathFinderTool(paths = images),ChoochChatTool()]
    prefix = """Have a conversation with a human, 
    Your role is to chat with an image.
    answering the following questions as best you can. You have access to the following tools:

    """
    suffix = """Begin!

    {chat_history}
    
    Question: {input}
    {agent_scratchpad}"""
    memory = CustomImageMemory(memory_key="chat_history",llm=chat_llm)
    prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=prefix,
        suffix=suffix,
        input_variables=["input", "chat_history", "agent_scratchpad"]
    )
    
    llm_chain = LLMChain(llm=OpenAI(temperature=0,streaming=True), prompt=prompt)
    agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
    
    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=True, memory=memory,return_intermediate_steps=True
    )

    return agent_chain