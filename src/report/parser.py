"""Report parsing utilities for SRAG reports."""

from common.config import REPORT_SUMMARY_MAX_CHARS, REPORT_SUMMARY_PARAGRAPH_LENGTH

# Headers and separators for extraction; change if report template changes
PARSER_HEADER_PREFIX = "Relatório SRAG"
PARSER_HEADER_SEP = "—"
PARSER_STOP_SECTIONS = ("Gráfico", "Visualizações", "Fontes")


def _extract_location(lines: list[str]) -> str | None:
    """Extract location from report header."""
    for line in lines:
        if PARSER_HEADER_PREFIX in line and PARSER_HEADER_SEP in line:
            return line.split(PARSER_HEADER_SEP)[-1].strip()
    return None


def _extract_report_body(lines: list[str]) -> str:
    """Extract report body text, stopping at charts/sources sections."""
    report_body_lines = []
    for line in lines:
        if line.strip().startswith("##") and any(
            s in line for s in PARSER_STOP_SECTIONS
        ):
            break
        if line.strip().startswith("---"):
            break
        if (
            line.strip()
            and not line.startswith("#")
            and not line.startswith("**Gerado")
        ):
            report_body_lines.append(line.strip())
    return " ".join(report_body_lines)


def _build_paragraphs(text: str) -> list[str]:
    """Build paragraphs from text, splitting by double newlines or creating from sentences."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if paragraphs:
        return paragraphs

    sentences = [s.strip() + "." for s in text.split(". ") if s.strip()]
    paragraphs = []
    current_para = []
    for sent in sentences:
        current_para.append(sent)
        if len(" ".join(current_para)) > REPORT_SUMMARY_PARAGRAPH_LENGTH:
            paragraphs.append(" ".join(current_para))
            current_para = []
    if current_para:
        paragraphs.append(" ".join(current_para))

    return paragraphs


def _build_summary_text(paragraphs: list[str]) -> str:
    """Build summary text from paragraphs, respecting max character limit."""
    summary_text = ""
    char_count = 0
    for para in paragraphs[:3]:
        if char_count + len(para) > REPORT_SUMMARY_MAX_CHARS:
            break
        if summary_text:
            summary_text += "\n\n"
        summary_text += para
        char_count += len(para)
    return summary_text


def generate_report_summary(report_content: str) -> str:
    """
    Generate formatted markdown summary from integrated report content for chat display.

    Args:
        report_content: Full markdown report content

    Returns:
        Formatted markdown summary for chat display (in Portuguese)

    """
    lines = report_content.split("\n")
    location = _extract_location(lines)
    report_body = _extract_report_body(lines)

    summary_parts = []
    if location:
        summary_parts.append(f"## Relatório SRAG: {location}")
    else:
        summary_parts.append("## Relatório SRAG")
    summary_parts.append("")

    if report_body:
        paragraphs = _build_paragraphs(report_body)
        summary_text = _build_summary_text(paragraphs)

        if summary_text:
            summary_parts.append(summary_text)
            summary_parts.append("")

    summary_parts.append("*Relatório completo disponível para download abaixo.*")

    if len(summary_parts) <= 2:
        return "## Relatório SRAG\n\nRelatório gerado com análises integradas de métricas, gráficos e notícias.\n\n*Relatório completo disponível para download abaixo.*"

    return "\n".join(summary_parts)
