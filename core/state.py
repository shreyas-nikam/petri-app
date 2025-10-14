import streamlit as st

def init_state():
    defaults = {
        # instruction UI
        "mode": "Choose from list",
        "chosen_instructions": [],
        "typed_instructions": "",
        # process/run
        "proc": None,           # multiprocessing.Process
        "log_q": None,          # mp.Queue for logs
        "is_running": False,
        "completed": False,
        "error_text": None,
        "exitcode": None,
        # run metadata
        "user_id": None,
        "run_dir": None,
        # streamed buffer
        "lines": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
