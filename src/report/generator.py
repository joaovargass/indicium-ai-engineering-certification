"""Report body generation for SRAG reports."""

from typing import Any

from common.config import REPORT_CONTENT_PREVIEW_LENGTH
from report.llm import _get_llm


def generate_report_body(
    metrics: dict[str, Any],
    news: list[dict],
    location: str,
    chart_info: dict[str, Any] | None = None,
    include_metrics: bool = True,
    include_news: bool = True,
    include_charts: bool = True,
) -> tuple[str, str]:
    """
    Generate integrated report body that weaves confirmed components into seamless narrative.

    IMPORTANT: Only includes components that were confirmed (via flags).

    Args:
        metrics: Dictionary with all 4 metrics (only used if include_metrics=True)
        news: List of news articles (only used if include_news=True)
        location: Location description
        chart_info: Optional dict with chart statistics (only used if include_charts=True)
        include_metrics: Whether metrics were confirmed for inclusion
        include_news: Whether news were confirmed for inclusion
        include_charts: Whether charts were confirmed for inclusion

    Returns:
        Tuple of (report_body, sources_section)
        - report_body: Integrated narrative text using only confirmed components
        - sources_section: Formatted sources list (only if include_news=True)

    """
    context_parts = _build_context_header(location)

    if include_metrics:
        context_parts.append(_build_metrics_context(metrics))

    if include_charts and chart_info:
        context_parts.append(_build_charts_context(chart_info))

    if include_news and news:
        context_parts.append(_build_news_context(news))

    instructions = _build_instructions(
        include_metrics, include_charts, include_news, chart_info, news
    )

    context = "".join(context_parts) + instructions

    try:
        llm = _get_llm()
        response = llm.invoke(context)
        report_body = response.content.strip()

        sources_section = _build_sources_section(news) if include_news and news else ""

        return report_body, sources_section
    except Exception:
        return _build_fallback_report(
            location, metrics, news, include_metrics, include_news
        )


def _build_context_header(location: str) -> list[str]:
    """Build the context header for the LLM prompt."""
    return [
        f"""Você é um analista de dados de saúde especializado em SRAG no Brasil.

Sua tarefa é criar um relatório profissional, fluido e integrado usando APENAS os dados confirmados abaixo. NÃO adicione informações que não foram fornecidas.

DADOS PARA {location}:
"""
    ]


def _build_metrics_context(metrics: dict[str, Any]) -> str:
    """Build metrics context for the LLM prompt."""
    case_data = metrics.get("case_increase", {})
    case_rate = case_data.get("rate")
    case_current = case_data.get("current_period_cases", 0)
    case_previous = case_data.get("previous_period_cases", 0)
    case_period_start = case_data.get("period_start")
    case_period_end = case_data.get("period_end")

    mortality_data = metrics.get("mortality", {})
    mortality_rate = mortality_data.get("rate")
    total_deaths = mortality_data.get("total_deaths", 0)
    total_cases = mortality_data.get("total_cases", 0)
    mortality_period_start = mortality_data.get("period_start")
    mortality_period_end = mortality_data.get("period_end")

    icu_data = metrics.get("icu_occupancy", {})
    icu_rate = icu_data.get("occupancy_rate")
    icu_patients = icu_data.get("patients_in_icu", 0)
    icu_beds = icu_data.get("total_icu_beds", 0)
    icu_period_start = icu_data.get("period_start")
    icu_period_end = icu_data.get("period_end")

    vax_data = metrics.get("vaccination", {})
    covid_vax = vax_data.get("covid_rate")
    flu_vax = vax_data.get("flu_rate")
    vax_period_start = vax_data.get("period_start")
    vax_period_end = vax_data.get("period_end")

    return f"""
Métricas Confirmadas:
- Taxa de aumento de casos: {case_rate}% (período atual: {case_current} casos, período anterior: {case_previous} casos)
  Período: {case_period_start} até {case_period_end}
- Taxa de mortalidade: {mortality_rate}% ({total_deaths} óbitos em {total_cases} casos)
  Período: {mortality_period_start} até {mortality_period_end}
- Taxa de ocupação de UTI: {icu_rate}% ({icu_patients} pacientes de {icu_beds} leitos)
  Período: {icu_period_start} até {icu_period_end}
- Taxa de vacinação COVID-19: {covid_vax}%
- Taxa de vacinação Gripe: {flu_vax}%
  Período: {vax_period_start} até {vax_period_end}
"""


def _format_daily_context(data: dict) -> str:
    """Format daily chart statistics for LLM context."""
    return f"""
Tendências dos Gráficos Confirmados (Casos Diários):
- Total de casos no período: {data.get("total_cases", 0)}
- Média diária: {data.get("avg_daily", 0):.1f} casos
- Pico diário: {data.get("max_daily", 0)} casos
- Tendência geral: {data.get("trend_direction", "estável")} ({data.get("trend_percentage", 0):.1f}% de mudança)
"""


def _format_monthly_context(data: dict) -> str:
    """Format monthly chart statistics for LLM context."""
    return f"""
Tendências dos Gráficos Confirmados (Casos Mensais):
- Total de casos no período: {data.get("total_cases", 0)}
- Média mensal: {data.get("avg_monthly", 0):.1f} casos
- Pico mensal: {data.get("max_monthly", 0)} casos
- Tendência geral: {data.get("trend_direction", "estável")} ({data.get("trend_percentage", 0):.1f}% de mudança)
"""


def _build_charts_context(chart_info: dict[str, Any]) -> str:
    """Build charts context for the LLM prompt."""
    if not isinstance(chart_info, dict):
        return ""

    parts = []

    if "daily" in chart_info:
        parts.append(_format_daily_context(chart_info["daily"]))
    elif chart_info.get("chart_type") == "daily":
        parts.append(_format_daily_context(chart_info))

    if "monthly" in chart_info:
        parts.append(_format_monthly_context(chart_info["monthly"]))
    elif chart_info.get("chart_type") == "monthly":
        parts.append(_format_monthly_context(chart_info))

    return "".join(parts)


def _build_news_context(news: list[dict]) -> str:
    """Build news context for the LLM prompt."""
    parts = ["\nNotícias Confirmadas para Contexto:\n"]

    for i, article in enumerate(news, 1):
        title = article.get("title", "Sem título")
        content = article.get("content", "")
        url = article.get("url", "")
        date = article.get("date", "")
        parts.append(f"""
{i}. {title}
   Conteúdo: {content[:REPORT_CONTENT_PREVIEW_LENGTH]}...
   Fonte: {url}
   Data: {date}
""")

    return "".join(parts)


def _components_text(
    include_metrics: bool,
    include_charts: bool,
    include_news: bool,
    chart_info: dict[str, Any] | None,
    news: list[dict] | None,
) -> str:
    """Build comma-separated list of included components for prompt."""
    components = []
    if include_metrics:
        components.append("métricas")
    if include_charts and chart_info:
        components.append("tendências dos gráficos")
    if include_news and news:
        components.append("notícias")
    return ", ".join(components) if components else "dados básicos"


def _build_integration_rules(
    include_metrics: bool,
    include_charts: bool,
    include_news: bool,
    chart_info: dict[str, Any] | None,
    news: list[dict] | None,
) -> str:
    """Build integration rules section of the prompt."""
    rules = "3. INTEGRAÇÃO:\n"

    if include_metrics:
        rules += """   - Interprete os dados das métricas e explique o que significam
   - SEMPRE mencione o período analisado nas explicações (e.g., "nos últimos 12 meses", "no período de 7 dias", "nos últimos 30 dias")
   - NUNCA mencione o formato de data (YYYY-MM-DD) explicitamente - apenas use datas naturalmente
   - Se a data máxima dos dados (period_end) for diferente da data de hoje, SEMPRE adicione uma nota mencionando "Estes são os dados disponíveis atualmente" ou similar
"""

    if include_charts and chart_info:
        has_both = isinstance(chart_info, dict) and (
            "daily" in chart_info or "monthly" in chart_info
        )
        chart_text = "gráficos diários e mensais" if has_both else "gráficos"
        rules += f"   - Integre insights dos {chart_text} (tendências, picos, padrões) naturalmente no texto\n"

    if include_news and news:
        rules += """   - Use as notícias para contextualizar e explicar os dados, não apenas listá-las
   - Conecte notícias aos dados quando ajudarem a entender as métricas
   - Se uma notícia contradiz os dados, explique a discrepância
"""
    return rules


def _narrative_rules(
    include_metrics: bool,
    include_charts: bool,
    include_news: bool,
    chart_info: dict[str, Any] | None,
    news: list[dict] | None,
) -> str:
    """Build narrative flow rules section of the prompt."""
    rules = """5. FLUXO NARRATIVO (COM MARKDOWN):
   - Comece com ## Visão Geral - apresente o contexto geral
"""
    if include_metrics:
        rules += "   - Integre métricas explicando o que significam no contexto\n"

    if include_charts and chart_info:
        has_both = isinstance(chart_info, dict) and (
            "daily" in chart_info or "monthly" in chart_info
        )
        chart_text = "gráficos diários e mensais" if has_both else "gráficos"
        rules += f"   - Use dados dos {chart_text} para apoiar as conclusões sobre tendências\n"

    if include_news and news:
        rules += "   - Use notícias para fornecer contexto externo quando relevante\n"

    rules += "   - Conclua com implicações e recomendações baseadas em todos os dados fornecidos\n"
    return rules


def _build_instructions(
    include_metrics: bool,
    include_charts: bool,
    include_news: bool,
    chart_info: dict[str, Any] | None,
    news: list[dict] | None,
) -> str:
    """
    Build complete instruction section for the LLM report generation prompt.

    Args:
        include_metrics: Whether metrics should be included
        include_charts: Whether charts should be included
        include_news: Whether news should be included
        chart_info: Chart statistics dictionary
        news: List of news articles

    Returns:
        Complete instructions string for LLM prompt

    """
    components_text = _components_text(
        include_metrics, include_charts, include_news, chart_info, news
    )

    base_instructions = f"""
INSTRUÇÕES CRÍTICAS PARA O RELATÓRIO:

1. USAR APENAS DADOS CONFIRMADOS: Você recebeu {components_text}. Use APENAS esses dados. NÃO invente, NÃO adicione informações que não foram fornecidas.

2. FORMATAÇÃO MARKDOWN OBRIGATÓRIA:
   - Use cabeçalhos markdown (##) para cada seção principal
   - Estrutura obrigatória:
     * ## Visão Geral
     * ## Análise das Métricas (se métricas incluídas)
     * ## Tendências dos Gráficos (se gráficos incluídos)
     * ## Contexto e Notícias (se notícias incluídas)
     * ## Implicações e Recomendações
   - Separe parágrafos com linha em branco
   - Use **negrito** para valores importantes: **11,5%**, **54,8%**
   - Use listas com marcadores (-) quando apropriado
   - Cada seção deve ter 1-2 parágrafos bem estruturados

"""

    integration_rules = _build_integration_rules(
        include_metrics, include_charts, include_news, chart_info, news
    )

    news_interpretation = """4. INTERPRETAÇÃO DAS NOTÍCIAS (se incluídas):
   - NÃO liste notícias como itens separados
   - Use o conteúdo das notícias para explicar e contextualizar os dados
   - Mencione insights relevantes das notícias quando ajudarem a entender as métricas

"""

    narrative_flow = _narrative_rules(
        include_metrics, include_charts, include_news, chart_info, news
    )

    formatting_rules = """
6. REGRAS DE FORMATAÇÃO:
   - SEMPRE use ## antes de cada seção (não use texto simples como título)
   - SEMPRE separe parágrafos com linha em branco
   - Use **negrito** para valores: **taxa de mortalidade de 11,5%**
   - Seja profissional mas acessível
   - Mínimo 4 seções, máximo 6 seções
   - Cada seção: 1-2 parágrafos
   - NUNCA mencione formato de data (YYYY-MM-DD) explicitamente - apenas use datas naturalmente

7. FONTES:
   - NÃO liste fontes no corpo do texto
   - NÃO mencione URLs ou links no texto principal
   - As fontes serão adicionadas automaticamente no final

Relatório Integrado (OBRIGATÓRIO: use ## para cada seção):"""

    return (
        base_instructions
        + integration_rules
        + news_interpretation
        + narrative_flow
        + formatting_rules
    )


def _build_sources_section(news: list[dict]) -> str:
    """Build the sources section from news articles."""
    sources = []
    for article in news:
        title = article.get("title", "Sem título")
        url = article.get("url", "")
        if url:
            clean_title = " ".join(title.split())
            sources.append(f"[{clean_title}]({url})")

    if sources:
        sources_list = "\n".join(f"- {source}" for source in sources)
        return f"\n\n## Fontes\n\n{sources_list}\n"

    return ""


def _build_fallback_report(
    location: str,
    metrics: dict[str, Any],
    news: list[dict],
    include_metrics: bool,
    include_news: bool,
) -> tuple[str, str]:
    """Build a fallback report when LLM fails."""
    fallback_parts = [
        "## Visão Geral\n",
        f"Análise dos dados SRAG para {location}.",
    ]

    if include_metrics:
        case_rate = metrics.get("case_increase", {}).get("rate")
        mortality_rate = metrics.get("mortality", {}).get("rate")
        icu_rate = metrics.get("icu_occupancy", {}).get("occupancy_rate")
        fallback_parts.append(
            f"\n\n## Análise das Métricas\n\n"
            f"Os dados indicam uma taxa de aumento de casos de **{case_rate}%**, "
            f"taxa de mortalidade de **{mortality_rate}%**, e ocupação de UTI de **{icu_rate}%**."
        )

    fallback_parts.append(
        "\n\n## Implicações e Recomendações\n\nA situação requer monitoramento contínuo."
    )
    fallback = "\n".join(fallback_parts)

    sources_section = ""
    if include_news and news:
        sources = []
        for article in news:
            title = article.get("title", "Sem título")
            url = article.get("url", "")
            if url:
                clean_title = " ".join(title.split())
                sources.append(f"[{clean_title}]({url})")
        if sources:
            sources_list = "\n".join(f"- {source}" for source in sources)
            sources_section = f"\n\n## Fontes\n\n{sources_list}\n"

    return fallback, sources_section
