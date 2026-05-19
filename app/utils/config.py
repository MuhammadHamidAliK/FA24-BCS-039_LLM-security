from functools import lru_cache
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


@lru_cache
def load_config() -> dict:
    with open(ROOT / "config" / "gateway_config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)
