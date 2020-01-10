from typing import Dict


def append_value(d: Dict, k: str, v: str) -> None:
    d[k] = v if d.get(k) is None else '{} {}'.format(d[k], v)
