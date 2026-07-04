"""Small shared helpers for Claude API responses."""

import re

# Em/en dashes are banned in customer-facing copy (they read as AI-written).
# The prompts already forbid them; this is the belt-and-braces layer for
# anything the model slips through.
_RANGE_DASH = re.compile(r"(?<=\d)\s*[–—]\s*(?=\d)")
_PROSE_DASH = re.compile(r"\s*[–—]\s*")


def humanize(text: str) -> str:
    """Strip em/en dashes from generated copy: digit ranges get a hyphen,
    prose gets a comma."""
    if not text or ("–" not in text and "—" not in text):
        return text
    text = _RANGE_DASH.sub("-", text)
    return _PROSE_DASH.sub(", ", text)


# Characters that could be the start of a dash pattern spanning a chunk
# boundary: whitespace, the dashes themselves, and digits (for ranges).
_HOLD = re.compile(r"[\s0-9–—]+$")


class StreamHumanizer:
    """Incremental humanize() for streamed text.

    Holds back a short tail whenever a chunk ends mid-pattern (whitespace,
    dash, or digit) so " — " and "10–15" are cleaned even when they span
    chunk boundaries. Call feed() per chunk and flush() once at the end.
    """

    def __init__(self) -> None:
        self._pending = ""

    def feed(self, chunk: str) -> str:
        buf = self._pending + chunk
        m = _HOLD.search(buf)
        if m:
            emit, self._pending = buf[: m.start()], buf[m.start():]
        else:
            emit, self._pending = buf, ""
        return humanize(emit)

    def flush(self) -> str:
        out = humanize(self._pending)
        self._pending = ""
        return out


def response_text(response) -> str:
    """First text block's content — robust to thinking blocks preceding text.

    Newer models (Sonnet 5+) may emit a ThinkingBlock before the TextBlock;
    naive `response.content[0].text` crashes on those.
    """
    for block in getattr(response, "content", []) or []:
        if getattr(block, "type", None) == "text" or hasattr(block, "text"):
            text = getattr(block, "text", None)
            if isinstance(text, str):
                return text
    return ""
