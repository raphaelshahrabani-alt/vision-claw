"""`glasses logs problems`: only the warnings and errors from the voice program's console log, one short line each.

The console log is one long JSON record per line, which can't be read in a screenshot. This keeps the time,
the level and the first part of the message, and folds repeats into "(x3)".
"""
from __future__ import annotations

import json
import re

LEVELS = ("WARNING", "ERROR", "CRITICAL")
SHORTEN = 170


def short(message: str) -> str:
    """The start of a message, on one line. Long 'event loop blocked' notes keep only their first clause."""
    message = re.sub(r"\s+", " ", message).strip()
    message = re.sub(r'(event loop blocked for \d+ms) at ".*"?, line \d+, in ([\w.]+).*', r"\1 in \2", message)
    return message if len(message) <= SHORTEN else message[:SHORTEN - 1] + "…"


def problem_lines(text: str, limit: int = 40) -> list[str]:
    """Time, level and message of each warning or error, newest last, repeats folded."""
    lines: list[tuple[str, int]] = []
    for raw in text.splitlines():
        raw = raw.strip()
        if not raw.startswith("{"):
            continue
        try:
            record = json.loads(raw)
        except ValueError:
            continue
        level = str(record.get("level", "")).upper()
        if level not in LEVELS:
            continue
        stamp = str(record.get("timestamp", ""))[11:19]
        line = f"{stamp}Z {level[:4]} {short(str(record.get('message', '')))}"
        if lines and lines[-1][0] == line:
            lines[-1] = (line, lines[-1][1] + 1)
        else:
            lines.append((line, 1))
    return [f"{line}  (x{count})" if count > 1 else line for line, count in lines[-limit:]]
