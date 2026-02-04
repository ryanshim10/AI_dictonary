import configparser
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str) -> Dict[str, Any]:
    p = Path(config_path)
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    cp = configparser.ConfigParser()
    cp.read(config_path, encoding="utf-8")

    def sec(name: str) -> Dict[str, str]:
        if name not in cp:
            return {}
        return {k: v for k, v in cp[name].items()}

    cfg = {
        "llm": sec("llm"),
        "stt": sec("stt"),
        "output": sec("output"),
    }
    return cfg


def resolve_rel(base_dir: str, maybe_rel: str) -> str:
    p = Path(maybe_rel)
    if p.is_absolute():
        return str(p)
    return str((Path(base_dir) / p).resolve())
