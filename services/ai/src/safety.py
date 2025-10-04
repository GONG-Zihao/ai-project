from __future__ import annotations

from typing import Any, Dict

SENSITIVE_KEYWORDS = {"暴力", "极端", "违法"}


def evaluate(content: str) -> Dict[str, Any]:
    flags = [word for word in SENSITIVE_KEYWORDS if word in content]
    return {
        "is_safe": not flags,
        "flags": flags,
    }
