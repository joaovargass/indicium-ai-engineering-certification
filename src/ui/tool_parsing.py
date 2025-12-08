"""Tool message content parsing utilities."""

import ast
import json


def parse_tool_content(content: str | dict) -> dict | None:
    """Parse tool message content to dict."""
    if isinstance(content, dict):
        return content

    if not isinstance(content, str):
        return None

    content_stripped = content.strip()

    # Try JSON first
    try:
        parsed = json.loads(content_stripped)
        return parsed if isinstance(parsed, dict) else None
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback to literal eval
    try:
        result = ast.literal_eval(content_stripped)
        return result if isinstance(result, dict) else None
    except (ValueError, SyntaxError):
        return None


def extract_report_info(parsed: dict) -> tuple[str | None, str | None]:
    """Extract report file path and content from parsed tool output."""
    file_path = None
    content = None

    # generate_download_report output
    if "file_path" in parsed:
        file_path = parsed.get("file_path")
        content = parsed.get("report_summary") or parsed.get("report_content")
    # generate_chat_report output
    elif "report_text" in parsed:
        content = parsed.get("report_text")

    return file_path, content
