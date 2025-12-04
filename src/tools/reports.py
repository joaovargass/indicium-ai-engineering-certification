"""Report generation tools for SRAG situation reports."""

from datetime import datetime
from typing import Annotated, Any

from langchain_core.tools import tool

from tools.chart_tools import get_daily_chart_json, get_monthly_chart_json
from tools.location_utils import get_location_description
from tools.metric_tools import (
    get_case_increase_rate,
    get_icu_occupancy_rate,
    get_mortality_rate,
    get_vaccination_rate,
)
from tools.news import search_srag_news_tool


def _fetch_all_metrics(uf: str | None, city_code: str | None) -> dict[str, Any]:
    """Fetch all metrics for a location."""
    return {
        "case_increase": get_case_increase_rate.invoke(
            {"uf": uf, "city_code": city_code}
        ),
        "mortality": get_mortality_rate.invoke({"uf": uf, "city_code": city_code}),
        "icu_occupancy": get_icu_occupancy_rate.invoke(
            {"uf": uf, "city_code": city_code}
        ),
        "vaccination": get_vaccination_rate.invoke({"uf": uf, "city_code": city_code}),
    }


def _fetch_news(location_desc: str, include_news: bool) -> list[dict]:
    """Fetch news articles if requested."""
    if not include_news:
        return []
    try:
        return search_srag_news_tool.invoke(
            {"query": f"SRAG {location_desc}", "max_results": 5}
        )
    except Exception:
        return []


def _format_metric(value: float | int | None, suffix: str = "%") -> str:
    """Format metric value for display."""
    return f"{value}{suffix}" if value is not None else "Dados não disponíveis"


def _build_metrics_section(metrics: dict) -> list[str]:
    """Build metrics section of report."""
    m = metrics
    return [
        "## Métricas Principais",
        "",
        "### Taxa de Aumento de Casos",
        f"- **Taxa:** {_format_metric(m['case_increase'].get('rate'))}",
        f"- **Período atual:** {m['case_increase'].get('current_period_cases', 0)} casos",
        f"- **Período anterior:** {m['case_increase'].get('previous_period_cases', 0)} casos",
        "",
        "### Taxa de Mortalidade",
        f"- **Taxa:** {_format_metric(m['mortality'].get('rate'))}",
        f"- **Total de óbitos:** {m['mortality'].get('total_deaths', 0)}",
        f"- **Total de casos:** {m['mortality'].get('total_cases', 0)}",
        "",
        "### Taxa de Ocupação de UTI",
        f"- **Taxa de ocupação:** {_format_metric(m['icu_occupancy'].get('occupancy_rate'))}",
        f"- **Pacientes em UTI:** {m['icu_occupancy'].get('patients_in_icu', 0)}",
        f"- **Total de leitos:** {m['icu_occupancy'].get('total_icu_beds', 'N/A')}",
        "",
        "### Taxas de Vacinação",
        f"- **COVID-19:** {_format_metric(m['vaccination'].get('covid_rate'))}",
        f"- **Gripe:** {_format_metric(m['vaccination'].get('flu_rate'))}",
    ]


def _build_news_section(articles: list[dict], detailed: bool = True) -> list[str]:
    """Build news section of report."""
    if not articles:
        return []

    lines = ["", "## Notícias Recentes", ""]
    for article in articles:
        if detailed:
            lines.extend(
                [
                    f"### {article.get('title', 'Sem título')}",
                    f"- **Fonte:** {article.get('url', 'N/A')}",
                    f"- **Data:** {article.get('date', 'Não disponível')}",
                    f"- **Resumo:** {article.get('content', '')[:200]}...",
                    "",
                ]
            )
        else:
            lines.append(
                f"- [{article.get('title', 'Sem título')}]({article.get('url', '#')})"
            )
    return lines


@tool
def generate_download_report(
    uf: Annotated[str | None, "State code. None for national."] = None,
    city_code: Annotated[str | None, "IBGE city code. Overrides UF."] = None,
    days: Annotated[int, "Days for daily chart (default: 30)."] = 30,
    months: Annotated[int, "Months for monthly chart (default: 12)."] = 12,
    include_news: Annotated[bool, "Include news (default: True)."] = True,
) -> str:
    """Generate SRAG report in Markdown for download. Use for 'generate/download report'."""
    location_desc = get_location_description(uf, city_code)
    metrics = _fetch_all_metrics(uf, city_code)
    news = _fetch_news(location_desc, include_news)

    lines = [
        f"# Relatório SRAG — {location_desc}",
        f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
        "## Resumo Executivo",
        "",
        f"Análise consolidada dos dados SRAG para {location_desc}.",
        "",
        *_build_metrics_section(metrics),
        "",
        "## Visualizações",
        "",
        f"- **Gráfico Diário:** Últimos {days} dias",
        f"- **Gráfico Mensal:** Últimos {months} meses",
        *_build_news_section(news, detailed=True),
        "",
        "---",
        "**Fonte:** OpenDATASUS SRAG Dataset (2023-2025)",
        "*Gerado automaticamente pelo Agente SRAG.*",
    ]

    return "\n".join(lines)


@tool
def generate_chat_report(
    uf: Annotated[str | None, "State code. None for national."] = None,
    city_code: Annotated[str | None, "IBGE city code. Overrides UF."] = None,
    days: Annotated[int, "Days for daily chart (default: 30)."] = 30,
    months: Annotated[int, "Months for monthly chart (default: 12)."] = 12,
    include_news: Annotated[bool, "Include news (default: True)."] = True,
) -> dict[str, Any]:
    """Generate SRAG report with charts for chat. Use for 'show/display report'."""
    location_desc = get_location_description(uf, city_code)
    metrics = _fetch_all_metrics(uf, city_code)
    news = _fetch_news(location_desc, include_news)

    lines = [
        f"# Relatório SRAG — {location_desc}",
        f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
        *_build_metrics_section(metrics),
        "",
        "## Gráficos Interativos",
        *_build_news_section(news, detailed=False),
    ]

    return {
        "report_text": "\n".join(lines),
        "daily_chart_json": get_daily_chart_json.invoke({"uf": uf, "days": days}),
        "monthly_chart_json": get_monthly_chart_json.invoke(
            {"uf": uf, "months": months}
        ),
        "metrics": metrics,
        "news": news,
    }
