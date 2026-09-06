
from config import SERVICES

_BY_KEY = {svc["key"]: svc for svc in SERVICES}


def get_service_config(key: str) -> dict:
    try:
        return _BY_KEY[key]
    except KeyError as exc:
        raise KeyError(f"No service configured with key '{key}'") from exc
