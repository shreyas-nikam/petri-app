import os
from pathlib import Path
from datetime import datetime

def get_user_id() -> str:
    for k in ("USER", "USERNAME", "LOGNAME"):
        v = os.environ.get(k)
        if v:
            return v
    try:
        return os.getlogin()
    except Exception:
        return "anonymous"

def new_run_dir() -> Path:
    uid = get_user_id()
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    p = Path("outputs") / uid / f"run-{ts}"
    p.mkdir(parents=True, exist_ok=True)
    return p
