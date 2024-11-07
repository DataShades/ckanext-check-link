from __future__ import annotations

from typing import Any

from . import check, report


def get_actions() -> dict[str, Any]:
    return {
        **check.get_actions(),
        **report.get_actions(),
    }
