"""Formatting functions for SRAG reports."""

from typing import Any

from common.config import EXPLANATION_MAX_LENGTH, NEWS_SUMMARY_MAX_LENGTH
from report.llm import generate_metric_explanation


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
    rows.append(
        {
            "metric": "Taxa de Aumento de Casos",
            "value": f"{case_rate}%" if case_rate is not None else "N/A",
            "explanation": case_explanation,
        }
    )

    # Mortality rate
    mortality_data = metrics.get("mortality", {})
    mortality_rate = mortality_data.get("rate")
    mortality_explanation = generate_metric_explanation(
        "mortality_rate", mortality_rate, mortality_data, news
    )
    rows.append(
        {
            "metric": "Taxa de Mortalidade",
            "value": f"{mortality_rate}%" if mortality_rate is not None else "N/A",
            "explanation": mortality_explanation,
        }
    )

    # ICU occupancy
    icu_data = metrics.get("icu_occupancy", {})
    icu_rate = icu_data.get("occupancy_rate")
    icu_explanation = generate_metric_explanation(
        "icu_occupancy_rate", icu_rate, icu_data, news
    )
    rows.append(
        {
            "metric": "Taxa de Ocupação de UTI (SRAG)",
            "value": f"{icu_rate}%" if icu_rate is not None else "N/A",
            "explanation": icu_explanation,
        }
    )

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
    rows.append(
        {
            "metric": "Taxas de Vacinação",
            "value": f"COVID-19: {covid_vax}%, Gripe: {flu_vax}%"
            if covid_vax is not None and flu_vax is not None
            else "N/A",
            "explanation": vax_explanation,
        }
    )

    # Build table
    table_lines = [
        "| Métrica | Valor | Explicação Contextualizada |",
        "|---------|-------|---------------------------|",
    ]

    for row in rows:
        explanation = row["explanation"]
        if len(explanation) > EXPLANATION_MAX_LENGTH:
            explanation = explanation[: EXPLANATION_MAX_LENGTH - 3] + "..."
        table_lines.append(f"| {row['metric']} | {row['value']} | {explanation} |")

    formulas = """
### Como as métricas são calculadas

- **Taxa de Aumento de Casos:** (casos no período atual − casos no período anterior) / casos no período anterior × 100. Períodos de 7 dias; os últimos 7 dias são excluídos por atraso de notificação.
- **Taxa de Mortalidade:** óbitos (evolução para óbito) / casos com evolução conhecida × 100. Excluem-se casos com evolução ignorada.
- **Taxa de Ocupação de UTI (SRAG):** (Σ pacientes-dia em UTI por SRAG) / (Σ leitos-dia) × 100. Apenas casos SRAG; pacientes-dia: OpenDataSUS (SRAG); leitos: CNES; fim do período limitado pela data viva da fonte.
- **Taxas de Vacinação:** percentual de casos com vacinação COVID-19 ou gripe registrada entre os com resposta válida; excluem-se ignorados.
"""
    return "\n".join(table_lines) + formulas


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
                    f"- **Resumo:** {article.get('content', '')[:NEWS_SUMMARY_MAX_LENGTH]}...",
                    "",
                ]
            )
        else:
            lines.append(
                f"- [{article.get('title', 'Sem título')}]({article.get('url', '#')})"
            )

    return "\n".join(lines)
