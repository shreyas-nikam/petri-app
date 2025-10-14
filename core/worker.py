import os
import sys
import logging
import multiprocessing as mp
import json
import streamlit as st

from core.streams import QueueHandler, StreamToQueue

def _worker_eval(log_q: mp.Queue, instructions: list[str], run_dir: str, api_key_env: str):
    """Child process: configure models, run eval, stream logs/stdout/stderr to Queue."""
    # Heavy imports inside child
    try:
        from inspect_ai import eval as inspect_eval
        from inspect_ai.model import get_model, GenerateConfig
    except Exception as e:
        log_q.put(("ERR", f"Failed to import inspect_ai: {e}"))
        log_q.put(("DONE", 1))
        return

    # Logging -> queue
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    qh = QueueHandler(log_q)
    qh.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    root.handlers = [qh]


    api_key = ""
    if not api_key:
        log_q.put(("ERR", f"Missing API key in env var {api_key_env or 'OPENAI_API_KEY'}"))
        log_q.put(("DONE", 1))
        return

    MODEL = "openai/gpt-4o-mini"
    try:
        target_model = get_model(MODEL, api_key=api_key)
        auditor_model = get_model(
            MODEL, api_key=api_key, config=GenerateConfig(max_tokens=16_000, reasoning_tokens=8_000)
        )
        judge_model = get_model(
            MODEL, api_key=api_key, config=GenerateConfig(max_tokens=16_000, reasoning_tokens=8_000)
        )
    except Exception as e:
        log_q.put(("ERR", f"Model init failed: {e}"))
        log_q.put(("DONE", 1))
        return

    # Info banners (no on-disk instruction persistence)
    log_q.put(("OUT", f"[info] Instructions: {len(instructions)} line(s) provided\n"))
    log_q.put(("OUT", f"[info] Instructions: {instructions}\n"))

    # Run eval
    try:
        
        if st.session_state.mode == "Choose from predefined probes":
            import json
            cached_results_lookup = json.load(open("cached_results_lookup.json"))
            # make copies of the files in the run_dir
            import time
            for k, v in cached_results_lookup.items():
                if k in instructions:
                    import shutil
                    shutil.copy(v, run_dir)
                    time.sleep(1)
        else:
            rc = 0
            inspect_eval(
                "petri/audit",
                model_roles={
                    "target": target_model,
                    "auditor": auditor_model,
                    "judge": judge_model,
                },
                max_connections=2,
                max_retries=2,
                fail_on_error=2,
                task_args={
                    "max_turns": 2,
                    # pass as string to match original usage, but not persisted anywhere
                    "special_instructions": json.dumps(instructions),
                    "transcript_save_dir": run_dir,
                },
            )
        log_q.put(("OUT", "[info] Eval completed.\n"))
        log_q.put(("DONE", rc))
    except Exception as e:
        log_q.put(("ERR", f"Eval failed: {e}\n"))
        log_q.put(("DONE", 1))
