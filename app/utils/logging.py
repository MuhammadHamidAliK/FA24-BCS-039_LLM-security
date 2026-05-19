import json
from datetime import datetime, timezone
from pathlib import Path

from app.utils.config import ROOT, load_config


def audit_log(record: dict) -> None:
    cfg = load_config()
    path = ROOT / cfg["audit"]["log_path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {**record, "ts": datetime.now(timezone.utc).isoformat()}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
