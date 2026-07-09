"""
Formats LLM plain-text answers into simple HTML: '- ' lines become <ul><li>,
**bold** becomes <strong>, blank lines separate paragraphs. Kept minimal and
safe (input is our own LLM output, but we still escape raw HTML first).
"""
import html
import re


def format_answer(text: str) -> str:
    if not text:
        return ""

    text = html.escape(text)
    # bold: **x** -> <strong>x</strong>
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    lines = [ln.rstrip() for ln in text.split("\n")]
    out = []
    in_list = False

    for ln in lines:
        stripped = ln.strip()
        is_bullet = stripped.startswith("- ") or stripped.startswith("* ")
        if is_bullet:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{stripped[2:].strip()}</li>")
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            if stripped:
                out.append(f"<p>{stripped}</p>")

    if in_list:
        out.append("</ul>")

    return "\n".join(out)
