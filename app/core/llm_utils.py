"""Small shared helpers for Claude API responses."""


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
