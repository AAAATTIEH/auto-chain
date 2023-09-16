
from utils.session_state import *
def func_reset_messages():
    try:
        messages_session_state().clear()
        executor_session_state().memory.clear() 
    except:
        print('No Memory for agent')
