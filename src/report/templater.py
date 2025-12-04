"""Report templating and LLM-based text generation for SRAG reports.

This module provides:
- Jinja2 templates for report structure
- LLM integration for generating contextualized explanations
- Validation functions
- Download functionality
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Template
from langchain_openai import ChatOpenAI

# LLM instance for generating explanations (lazy initialization)
_llm: ChatOpenAI | None = None


def _get_llm() -> ChatOpenAI:
    """Get or create LLM instance (lazy initialization)."""
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-5-nano", temperature=0.3)
    return _llm


def validate_report_request(
    days: int,
    months: int,
    max_news: int,
) -> tuple[bool, str]:
    """
    Validate report generation request parameters.

    Args:
        days: Days for daily chart
        months: Months for monthly chart
        max_news: Maximum number of news articles

    Returns:
        Tuple of (is_valid, error_message)
    """
    if days < 7 or days > 90:
        return False, "Days must be between 7 and 90"

    if months < 1 or months > 24:
        return False, "Months must be between 1 and 24"

    if max_news < 0 or max_news > 5:
        return False, "Maximum 5 news articles allowed (0-5)"

    return True, ""


def generate_executive_summary(
    metrics: dict[str, Any],
    news: list[dict],
    location: str,
) -> str:
    """
    Generate executive summary using LLM based on metrics and news.

    Args:
        metrics: Dictionary with all 4 metrics
        news: List of news articles
        location: Location description

    Returns:
        LLM-generated executive summary text
    """
    # Prepare context for LLM
    case_rate = metrics.get("case_increase", {}).get("rate")
    mortality_rate = metrics.get("mortality", {}).get("rate")
    icu_rate = metrics.get("icu_occupancy", {}).get("occupancy_rate")
    covid_vax = metrics.get("vaccination", {}).get("covid_rate")
    flu_vax = metrics.get("vaccination", {}).get("flu_rate")

    # Build prompt for LLM
    prompt = f"""Você é um analista de dados de saúde especializado em SRAG no Brasil.

Com base nos dados abaixo, gere um resumo executivo profissional e conciso (2-3 parágrafos) em português.

Dados para {location}:
- Taxa de aumento de casos: {case_rate}%
- Taxa de mortalidade: {mortality_rate}%
- Taxa de ocupação de UTI: {icu_rate}%
- Taxa de vacinação COVID-19: {covid_vax}%
- Taxa de vacinação Gripe: {flu_vax}%

"""

    if news:
        prompt += "Notícias relevantes:\n"
        for article in news[:3]:  # Use max 3 for context
            prompt += f"- {article.get('title', '')}: {article.get('content', '')[:150]}...\n"
        prompt += "\n"

    prompt += """Instruções:
- Gere um resumo executivo que sintetize os dados principais
- Destaque tendências importantes (aumento/diminuição)
- Conecte os dados às notícias quando relevante
- Seja profissional e claro
- Máximo 3 parágrafos
- Foque no que os dados significam para a situação atual

Resumo Executivo:"""

    try:
        llm = _get_llm()
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        # Fallback if LLM fails
        return f"Análise consolidada dos dados SRAG para {location}. Os dados indicam uma situação que requer monitoramento contínuo."


def generate_metric_explanation(
    metric_name: str,
    metric_value: Any,
    metric_data: dict[str, Any],
    news: list[dict],
) -> str:
    """
    Generate contextualized explanation for a metric using LLM.

    Args:
        metric_name: Name of the metric (e.g., "case_increase_rate")
        metric_value: The metric value
        metric_data: Full metric data dictionary
        news: List of relevant news articles

    Returns:
        LLM-generated explanation text (1-2 sentences)
    """
    # Map metric names to Portuguese
    metric_names_pt = {
        "case_increase_rate": "Taxa de Aumento de Casos",
        "mortality_rate": "Taxa de Mortalidade",
        "icu_occupancy_rate": "Taxa de Ocupação de UTI",
        "vaccination_rate": "Taxa de Vacinação",
    }

    metric_name_pt = metric_names_pt.get(metric_name, metric_name)

    # Build context string
    context = f"Métrica: {metric_name_pt}\n"
    context += f"Valor: {metric_value}\n"

    # Add relevant details based on metric type
    if metric_name == "case_increase_rate":
        context += f"Casos no período atual: {metric_data.get('current_period_cases', 0)}\n"
        context += f"Casos no período anterior: {metric_data.get('previous_period_cases', 0)}\n"
    elif metric_name == "mortality_rate":
        context += f"Total de óbitos: {metric_data.get('total_deaths', 0)}\n"
        context += f"Total de casos: {metric_data.get('total_cases', 0)}\n"
    elif metric_name == "icu_occupancy_rate":
        context += f"Pacientes em UTI: {metric_data.get('patients_in_icu', 0)}\n"
        context += f"Total de leitos: {metric_data.get('total_icu_beds', 'N/A')}\n"
    elif metric_name == "vaccination_rate":
        context += f"Vacinação COVID-19: {metric_data.get('covid_rate', 0)}%\n"
        context += f"Vacinação Gripe: {metric_data.get('flu_rate', 0)}%\n"

    # Add relevant news (max 2)
    if news:
        context += "\nNotícias relevantes:\n"
        for article in news[:2]:
            context += f"- {article.get('title', '')}\n"

    prompt = f"""Você é um analista de dados de saúde. 

Com base nos dados abaixo, gere uma explicação contextualizada curta (1-2 frases) em português que explique o que este valor significa no cenário atual.

{context}

Instruções:
- Explique o que o valor significa (alto, baixo, preocupante, positivo, etc.)
- Conecte às notícias se relevante
- Seja claro e profissional
- Máximo 2 frases

Explicação:"""

    try:
        response = _llm.invoke(prompt)
        return response.content.strip()
    except Exception:
        # Fallback explanation
        return f"Este valor indica a situação atual da {metric_name_pt.lower()} no período analisado."


def format_metrics_table(metrics: dict[str, Any], news: list[dict]) -> str:
    """
    Format metrics as a professional Markdown table with LLM-generated explanations.

    Args:
        metrics: Dictionary with all 4 metrics
        news: List of news articles for context

    Returns:
        Markdown table string
    """
    rows = []

    # Case increase rate
    case_data = metrics.get("case_increase", {})
    case_rate = case_data.get("rate")
    case_explanation = generate_metric_explanation(
        "case_increase_rate", case_rate, case_data, news
    )
    rows.append({
        "metric": "Taxa de Aumento de Casos",
        "value": f"{case_rate}%" if case_rate is not None else "N/A",
        "explanation": case_explanation,
    })

    # Mortality rate
    mortality_data = metrics.get("mortality", {})
    mortality_rate = mortality_data.get("rate")
    mortality_explanation = generate_metric_explanation(
        "mortality_rate", mortality_rate, mortality_data, news
    )
    rows.append({
        "metric": "Taxa de Mortalidade",
        "value": f"{mortality_rate}%" if mortality_rate is not None else "N/A",
        "explanation": mortality_explanation,
    })

    # ICU occupancy
    icu_data = metrics.get("icu_occupancy", {})
    icu_rate = icu_data.get("occupancy_rate")
    icu_explanation = generate_metric_explanation(
        "icu_occupancy_rate", icu_rate, icu_data, news
    )
    rows.append({
        "metric": "Taxa de Ocupação de UTI",
        "value": f"{icu_rate}%" if icu_rate is not None else "N/A",
        "explanation": icu_explanation,
    })

    # Vaccination
    vax_data = metrics.get("vaccination", {})
    covid_vax = vax_data.get("covid_rate")
    flu_vax = vax_data.get("flu_rate")
    vax_explanation = generate_metric_explanation(
        "vaccination_rate",
        f"COVID-19: {covid_vax}%, Gripe: {flu_vax}%",
        vax_data,
        news,
    )
    rows.append({
        "metric": "Taxas de Vacinação",
        "value": f"COVID-19: {covid_vax}%, Gripe: {flu_vax}%"
        if covid_vax is not None and flu_vax is not None
        else "N/A",
        "explanation": vax_explanation,
    })

    # Build table
    table_lines = [
        "| Métrica | Valor | Explicação Contextualizada |",
        "|---------|-------|---------------------------|",
    ]

    for row in rows:
        # Truncate explanation if too long
        explanation = row["explanation"]
        if len(explanation) > 100:
            explanation = explanation[:97] + "..."
        table_lines.append(
            f"| {row['metric']} | {row['value']} | {explanation} |"
        )

    return "\n".join(table_lines)


def format_news_section(articles: list[dict], detailed: bool = True) -> str:
    """
    Format news articles section.

    Args:
        articles: List of news article dictionaries
        detailed: If True, include full details; if False, just links

    Returns:
        Markdown formatted news section
    """
    if not articles:
        return ""

    lines = ["## Notícias Recentes", ""]

    for article in articles:
        if detailed:
            lines.extend(
                [
                    f"### {article.get('title', 'Sem título')}",
                    f"- **Fonte:** [{article.get('url', 'N/A')}]({article.get('url', '#')})",
                    f"- **Data:** {article.get('date', 'Não disponível')}",
                    f"- **Resumo:** {article.get('content', '')[:200]}...",
                    "",
                ]
            )
        else:
            lines.append(
                f"- [{article.get('title', 'Sem título')}]({article.get('url', '#')})"
            )

    return "\n".join(lines)


def render_report_template(
    location: str,
    executive_summary: str,
    metrics_table: str,
    charts_section: str,
    news_section: str,
    include_executive_summary: bool = True,
    include_metrics: bool = True,
    include_charts: bool = True,
    include_news: bool = True,
) -> str:
    """
    Render report using Jinja2 template.

    Args:
        location: Location description
        executive_summary: LLM-generated executive summary
        metrics_table: Formatted metrics table
        charts_section: Charts description section
        news_section: News section
        include_executive_summary: Whether to include executive summary
        include_metrics: Whether to include metrics
        include_charts: Whether to include charts
        include_news: Whether to include news

    Returns:
        Complete report as Markdown string
    """
    template_str = """# Relatório SRAG — {{ location }}
**Gerado em:** {{ generation_date }}

{% if include_executive_summary %}
## Resumo Executivo

{{ executive_summary }}

{% endif %}
{% if include_metrics %}
## Métricas Principais

{{ metrics_table }}

{% endif %}
{% if include_charts %}
## Visualizações

{{ charts_section }}

{% endif %}
{% if include_news and news_section %}
{{ news_section }}

{% endif %}
---

**Fonte:** OpenDATASUS SRAG Dataset (2023-2025)
*Gerado automaticamente pelo Agente SRAG com análises contextualizadas.*
"""

    template = Template(template_str)
    generation_date = datetime.now().strftime("%d/%m/%Y %H:%M")

    return template.render(
        location=location,
        generation_date=generation_date,
        executive_summary=executive_summary,
        metrics_table=metrics_table,
        charts_section=charts_section,
        news_section=news_section,
        include_executive_summary=include_executive_summary,
        include_metrics=include_metrics,
        include_charts=include_charts,
        include_news=include_news,
    )


def save_report_to_file(
    report_content: str,
    location: str,
    output_dir: Path | None = None,
) -> Path:
    """
    Save report to file for download.

    Args:
        report_content: Markdown report content
        location: Location name (for filename)
        output_dir: Directory to save reports (default: reports/ in project root)

    Returns:
        Path to saved file
    """
    if output_dir is None:
        # Default to reports/ directory in project root
        project_root = Path(__file__).resolve().parent.parent.parent
        output_dir = project_root / "reports"

    # Create directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename: sanitize location name
    location_safe = location.replace(" ", "_").replace("/", "_").replace("\\", "_")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"relatorio_srag_{location_safe}_{timestamp}.md"
    file_path = output_dir / filename

    # Save file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return file_path

