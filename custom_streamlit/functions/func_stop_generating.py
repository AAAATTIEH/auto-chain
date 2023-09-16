from utils.session_state import *
def func_stop_generating():
    max_iterations = executor_session_state().max_iterations
    executor_session_state().max_iterations = 0
    executor_session_state().max_iterations = max_iterations
    st.session_state['executing'] = 'Forced'
    st.session_state.max_iterations = max_iterations
    st.experimental_rerun()
  