import gc
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
from streamlit.runtime.runtime import Runtime

# ...

def st_runtime():

    global _st_runtime

    if _st_runtime:
        return _st_runtime

    for obj in gc.get_objects():
        if type(obj) is Runtime:
            _st_runtime = obj
            return _st_runtime

_st_runtime = None

# ...

def session_id():

    script_run_ctx = get_script_run_ctx()
    return script_run_ctx.session_id if script_run_ctx else ''

# ...

runtime = st_runtime()

if runtime:
    session_info = runtime.get_client(session_id=session_id())
    if session_info:
        request = getattr(session_info, 'request')
        host_name = request.host_name
        remote_ip = request.remote_ip
        headers = request.headers
