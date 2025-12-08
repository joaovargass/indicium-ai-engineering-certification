"""LLM integration for SRAG reports."""

from typing import Any

from langchain_openai import ChatOpenAI

from common.config import ARTICLE_PREVIEW_LENGTH, DEFAULT_MODEL_NAME, REPORT_TEMPERATURE

# LLM instance for generating explanations (lazy initialization)
_llm: ChatOpenAI | None = None


def _get_llm() -> ChatOpenAI:
    """Get or create LLM instance (lazy initialization)."""
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model=DEFAULT_MODEL_NAME, temperature=REPORT_TEMPERATURE)
    return _llm


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
    case_rate = metrics.get("case_increase", {}).get("rate")
    mortality_rate = metrics.get("mortality", {}).get("rate")
    icu_rate = metrics.get("icu_occupancy", {}).get("occupancy_rate")
    covid_vax = metrics.get("vaccination", {}).get("covid_rate")
    flu_vax = metrics.get("vaccination", {}).get("flu_rate")

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
        for article in news[:3]:
            prompt += f"- {article.get('title', '')}: {article.get('content', '')[:ARTICLE_PREVIEW_LENGTH]}...\n"
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
    except Exception:
        return f"Análise consolidada dos dados SRAG para {location}. Os dados indicam uma situação que requer monitoramento contínuo."


def _build_metric_context(
    metric_name: str,
    metric_name_pt: str,
    metric_value: int | float | str | None,
    metric_data: dict[str, Any],
    news: list[dict],
) -> str:
    """Build context string for metric explanation prompt."""
    context = f"Métrica: {metric_name_pt}\n"
    context += f"Valor: {metric_value}\n"

    if metric_name == "case_increase_rate":
        context += (
            f"Casos no período atual: {metric_data.get('current_period_cases', 0)}\n"
        )
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

    if news:
        context += "\nNotícias relevantes:\n"
        for article in news[:2]:
            context += f"- {article.get('title', '')}\n"

    return context


def _check_data_outdated(period_end: str | None) -> str:
    """Check if data is outdated and return note if needed."""
    if not period_end:
        return ""

    from datetime import datetime

    today = datetime.now().date()
    try:
        period_end_date = datetime.fromisoformat(
            period_end.replace("Z", "+00:00")
        ).date()
        if period_end_date < today:
            return "\nIMPORTANTE: A data máxima dos dados é diferente da data de hoje. Você DEVE mencionar 'Estes são os dados disponíveis atualmente' ou similar na explicação."
    except Exception:
        pass

    return ""


def generate_metric_explanation(
    metric_name: str,
    metric_value: int | float | str | None,
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
    metric_names_pt = {
        "case_increase_rate": "Taxa de Aumento de Casos",
        "mortality_rate": "Taxa de Mortalidade",
        "icu_occupancy_rate": "Taxa de Ocupação de UTI",
        "vaccination_rate": "Taxa de Vacinação",
    }

    metric_name_pt = metric_names_pt.get(metric_name, metric_name)
    context = _build_metric_context(
        metric_name, metric_name_pt, metric_value, metric_data, news
    )

    period_start = metric_data.get("period_start")
    period_end = metric_data.get("period_end")
    period_info = ""
    if period_start and period_end:
        period_info = f"\nPeríodo analisado: {period_start} até {period_end}"

    data_outdated_note = _check_data_outdated(period_end)

    prompt = f"""Você é um analista de dados de saúde.

Com base nos dados abaixo, gere uma explicação contextualizada curta (2-3 frases) em português que explique o que este valor significa no cenário atual.

{context}{period_info}{data_outdated_note}

Instruções:
- Explique o que o valor significa (alto, baixo, preocupante, positivo, etc.)
- SEMPRE mencione o período analisado na explicação (e.g., "nos últimos 12 meses", "no período de 7 dias", "nos últimos 30 dias")
- NUNCA mencione o formato de data (YYYY-MM-DD) explicitamente - apenas use datas naturalmente
- Se a data máxima dos dados for diferente da data de hoje, SEMPRE adicione uma nota mencionando "Estes são os dados disponíveis atualmente" ou similar
- Conecte às notícias se relevante
- Seja claro e profissional
- Máximo 2-3 frases

Explicação:"""

    try:
        llm = _get_llm()
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception:
        return f"Este valor indica a situação atual da {metric_name_pt.lower()} no período analisado."
