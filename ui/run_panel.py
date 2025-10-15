import os
import queue
import multiprocessing as mp
from pathlib import Path
import json

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from core.utils import new_run_dir
from core.worker import _worker_eval
from dotenv import load_dotenv
load_dotenv()

def _collect_instructions() -> list[str]:
    if st.session_state.mode == "Choose from predefined probes":
        return st.session_state.chosen_instructions or []
    # split by line, strip bullets/whitespace
    return st.session_state.typed_instructions

def _on_run():
    print("started run")
    if st.session_state.is_running:
        return

    print("collecting instructions")
    instr = _collect_instructions()
    print("instructions collected")
    print(instr)
    if not instr:
        st.error("Please provide at least one instruction (choose or type).")
        return

    run_dir = new_run_dir()
    st.session_state.run_dir = str(run_dir)

    # Context: spawn on Windows; fork on Unix
    if os.name == "nt":
        mp_ctx = mp.get_context("spawn")
    else:
        mp_ctx = mp.get_context("fork")

    q = mp_ctx.Queue()
    st.session_state.log_q = q

    api_key_env = os.environ.get("OPENAI_API_KEY", "")

    p = mp_ctx.Process(
        target=_worker_eval,
        args=(q, instr, str(run_dir), api_key_env),
        daemon=True,
    )
    p.start()
    st.session_state.proc = p
    st.session_state.is_running = True
    st.session_state.completed = False
    st.session_state.error_text = None
    st.session_state.exitcode = None
    st.session_state.lines = []
    st.toast("Eval started.", icon="▶️")

def _on_terminate():
    p = st.session_state.proc
    if p and st.session_state.is_running:
        try:
            p.terminate()
        except Exception as e:
            st.session_state.error_text = f"Terminate failed: {e}"
    st.session_state.is_running = False
    st.session_state.completed = True
    st.session_state.exitcode = -1
    st.toast("Process terminated.", icon="🛑")

def _stream_outputs():
    """Poll the queue and append lines to session state."""
    if st.session_state.is_running and st.session_state.log_q is not None:
        st_autorefresh(interval=800, key="autorefresh_eval")
        try:
            while True:
                tag, payload = st.session_state.log_q.get_nowait()
                if tag in ("OUT", "ERR"):
                    st.session_state.lines.append(payload)
                elif tag == "DONE":
                    st.session_state.exitcode = int(payload)
                    st.session_state.is_running = False
                    st.session_state.completed = True
        except queue.Empty:
            pass

def run_panel():
    c1, c2 = st.columns([1, 1])
    with c1:
        # disable the button if the chosen mode is predefined and no instructions are selected or if the chosen mode is typed and no instructions are typed or if the process is running
        is_button_disabled = st.session_state.is_running or (st.session_state.mode == "Choose from predefined probes" and not st.session_state.chosen_instructions) or (st.session_state.mode != "Choose from predefined probes" and not st.session_state.typed_instructions)
        st.button("Run Eval", type="primary", use_container_width=True, disabled=is_button_disabled, on_click=_on_run)
    with c2:
        st.button("Terminate", type="secondary", use_container_width=True, disabled=not st.session_state.is_running, on_click=_on_terminate)

    # ---- Loader + streamed outputs (replaces terminal UI) ----
    _stream_outputs()

    # Loader feel: sticky status + streaming text body
    status_box = st.container(border=True)
    with status_box:
        if st.session_state.is_running:
            st.markdown("**Status:** Running… ⏳")
        elif st.session_state.completed:
            if st.session_state.exitcode == 0:
                st.markdown("**Status:** Completed. ✅")
            elif st.session_state.exitcode == -1:
                st.markdown("**Status:** Terminated by user. ⚠️")
            else:
                st.markdown(f"**Status:** Completed with errors (exit code {st.session_state.exitcode}). ❌")
        else:
            st.markdown("**Status:** Idle")

        # Streamed lines (compact, monospaced)
        text = "".join(st.session_state.lines)
        if st.session_state.is_running:
            with st.spinner("Evaluating and streaming output…"):
                st.code(text or "[waiting for first chunk…]", language="text")
        else:
            st.code(text or "[no output]", language="text")
