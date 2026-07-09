"""
Prompt-injection defense ported from IntelliRAG.

Note: the fix documented in the IntelliRAG bug narrative is preserved -
the pattern uses '*' (not '?') so any number of modifier words between
"ignore" and "instructions" is caught.

Detection alone is not enough: callers MUST exclude flagged chunks from the
context before it reaches the LLM, not just log them.
"""
import re

INJECTION_PATTERNS = [
    r"ignore (all |any |previous |prior |these |the )*instructions",
    r"disregard (the |your )?(system|above) prompt",
    r"you are now",
    r"new instructions?:",
    r"reveal (the |your )?(system )?prompt",
    r"act as if",
    r"pretend (you are|to be)",
    r"override (your |the )?(rules|guidelines|restrictions)",
]


def scan_for_injection(text: str) -> list[str]:
    return [p for p in INJECTION_PATTERNS if re.search(p, text.lower())]
