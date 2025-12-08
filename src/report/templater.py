"""
Report templating and LLM-based text generation for SRAG reports.

This module provides:
- Jinja2 templates for report structure
- LLM integration for generating contextualized explanations
- Validation functions
- Download functionality
"""

import zipfile
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
            prompt += (
                f"- {article.get('title', '')}: {article.get('content', '')[:150]}...\n"
            )
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
        # Fallback if LLM fails
        return f"Análise consolidada dos dados SRAG para {location}. Os dados indicam uma situação que requer monitoramento contínuo."


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
            "metric": "Taxa de Ocupação de UTI",
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
        # Truncate explanation if too long
        explanation = row["explanation"]
        if len(explanation) > 100:
            explanation = explanation[:97] + "..."
        table_lines.append(f"| {row['metric']} | {row['value']} | {explanation} |")

    return "\n".join(table_lines)


def generate_integrated_report_body(
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
    # Build context - only include what was confirmed
    context_parts = [f"""Você é um analista de dados de saúde especializado em SRAG no Brasil.

Sua tarefa é criar um relatório profissional, fluido e integrado usando APENAS os dados confirmados abaixo. NÃO adicione informações que não foram fornecidas.

DADOS PARA {location}:
"""]

    # Add metrics only if confirmed
    if include_metrics:
        case_data = metrics.get("case_increase", {})
        case_rate = case_data.get("rate")
        case_current = case_data.get("current_period_cases", 0)
        case_previous = case_data.get("previous_period_cases", 0)
        
        mortality_data = metrics.get("mortality", {})
        mortality_rate = mortality_data.get("rate")
        total_deaths = mortality_data.get("total_deaths", 0)
        total_cases = mortality_data.get("total_cases", 0)
        
        icu_data = metrics.get("icu_occupancy", {})
        icu_rate = icu_data.get("occupancy_rate")
        icu_patients = icu_data.get("patients_in_icu", 0)
        icu_beds = icu_data.get("total_icu_beds", 0)
        
        vax_data = metrics.get("vaccination", {})
        covid_vax = vax_data.get("covid_rate")
        flu_vax = vax_data.get("flu_rate")
        
        context_parts.append(f"""
Métricas Confirmadas:
- Taxa de aumento de casos: {case_rate}% (período atual: {case_current} casos, período anterior: {case_previous} casos)
- Taxa de mortalidade: {mortality_rate}% ({total_deaths} óbitos em {total_cases} casos)
- Taxa de ocupação de UTI: {icu_rate}% ({icu_patients} pacientes de {icu_beds} leitos)
- Taxa de vacinação COVID-19: {covid_vax}%
- Taxa de vacinação Gripe: {flu_vax}%
""")

    # Add chart information only if confirmed
    if include_charts and chart_info:
        # Handle both single chart dict and dict with daily/monthly keys
        if isinstance(chart_info, dict):
            if "daily" in chart_info or "monthly" in chart_info:
                # Multiple charts
                if "daily" in chart_info:
                    daily = chart_info["daily"]
                    context_parts.append(f"""
Tendências dos Gráficos Confirmados (Casos Diários):
- Total de casos no período: {daily.get('total_cases', 0)}
- Média diária: {daily.get('avg_daily', 0):.1f} casos
- Pico diário: {daily.get('max_daily', 0)} casos
- Tendência geral: {daily.get('trend_direction', 'estável')} ({daily.get('trend_percentage', 0):.1f}% de mudança)
""")
                if "monthly" in chart_info:
                    monthly = chart_info["monthly"]
                    context_parts.append(f"""
Tendências dos Gráficos Confirmados (Casos Mensais):
- Total de casos no período: {monthly.get('total_cases', 0)}
- Média mensal: {monthly.get('avg_monthly', 0):.1f} casos
- Pico mensal: {monthly.get('max_monthly', 0)} casos
- Tendência geral: {monthly.get('trend_direction', 'estável')} ({monthly.get('trend_percentage', 0):.1f}% de mudança)
""")
            else:
                # Single chart dict
                chart_type = chart_info.get("chart_type", "")
                if chart_type == "daily":
                    context_parts.append(f"""
Tendências dos Gráficos Confirmados (Casos Diários):
- Total de casos no período: {chart_info.get('total_cases', 0)}
- Média diária: {chart_info.get('avg_daily', 0):.1f} casos
- Pico diário: {chart_info.get('max_daily', 0)} casos
- Tendência geral: {chart_info.get('trend_direction', 'estável')} ({chart_info.get('trend_percentage', 0):.1f}% de mudança)
""")
                elif chart_type == "monthly":
                    context_parts.append(f"""
Tendências dos Gráficos Confirmados (Casos Mensais):
- Total de casos no período: {chart_info.get('total_cases', 0)}
- Média mensal: {chart_info.get('avg_monthly', 0):.1f} casos
- Pico mensal: {chart_info.get('max_monthly', 0)} casos
- Tendência geral: {chart_info.get('trend_direction', 'estável')} ({chart_info.get('trend_percentage', 0):.1f}% de mudança)
""")

    # Add news only if confirmed
    if include_news and news:
        context_parts.append("\nNotícias Confirmadas para Contexto:\n")
        for i, article in enumerate(news, 1):
            title = article.get('title', 'Sem título')
            content = article.get('content', '')
            url = article.get('url', '')
            date = article.get('date', '')
            context_parts.append(f"""
{i}. {title}
   Conteúdo: {content[:300]}...
   Fonte: {url}
   Data: {date}
""")

    # Build instructions based on what's included
    included_components = []
    if include_metrics:
        included_components.append("métricas")
    if include_charts and chart_info:
        included_components.append("tendências dos gráficos")
    if include_news and news:
        included_components.append("notícias")
    
    components_text = ", ".join(included_components) if included_components else "dados básicos"
    
    instructions = f"""
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

3. INTEGRAÇÃO: 
"""
    
    if include_metrics:
        instructions += "   - Interprete os dados das métricas e explique o que significam\n"
    if include_charts and chart_info:
        if isinstance(chart_info, dict) and ("daily" in chart_info or "monthly" in chart_info):
            instructions += "   - Integre insights dos gráficos diários e mensais (tendências, picos, padrões) naturalmente no texto\n"
        else:
            instructions += "   - Integre insights dos gráficos (tendências, picos, padrões) naturalmente no texto\n"
    if include_news and news:
        instructions += """   - Use as notícias para contextualizar e explicar os dados, não apenas listá-las
   - Conecte notícias aos dados quando ajudarem a entender as métricas
   - Se uma notícia contradiz os dados, explique a discrepância
"""
    
    instructions += """4. INTERPRETAÇÃO DAS NOTÍCIAS (se incluídas):
   - NÃO liste notícias como itens separados
   - Use o conteúdo das notícias para explicar e contextualizar os dados
   - Mencione insights relevantes das notícias quando ajudarem a entender as métricas

5. FLUXO NARRATIVO (COM MARKDOWN):
   - Comece com ## Visão Geral - apresente o contexto geral
"""
    
    if include_metrics:
        instructions += "   - Integre métricas explicando o que significam no contexto\n"
    if include_charts and chart_info:
        if isinstance(chart_info, dict) and ("daily" in chart_info or "monthly" in chart_info):
            instructions += "   - Use dados dos gráficos diários e mensais para apoiar as conclusões sobre tendências\n"
        else:
            instructions += "   - Use dados dos gráficos para apoiar as conclusões sobre tendências\n"
    if include_news and news:
        instructions += "   - Use notícias para fornecer contexto externo quando relevante\n"
    
    instructions += """   - Conclua com implicações e recomendações baseadas em todos os dados fornecidos

6. EXEMPLO DE ESTRUTURA MARKDOWN:
```
## Visão Geral

[Parágrafo introdutório com contexto geral da situação]

## Análise das Métricas

[Parágrafos integrando métricas, explicando o que significam]

## Tendências dos Gráficos

[Parágrafos integrando insights dos gráficos]

## Contexto e Notícias

[Parágrafos usando notícias para contextualizar]

## Implicações e Recomendações

[Parágrafos com conclusões e recomendações]
```

7. REGRAS DE FORMATAÇÃO:
   - SEMPRE use ## antes de cada seção (não use texto simples como título)
   - SEMPRE separe parágrafos com linha em branco
   - Use **negrito** para valores: **taxa de mortalidade de 11,5%**
   - Seja profissional mas acessível
   - Mínimo 4 seções, máximo 6 seções
   - Cada seção: 1-2 parágrafos

8. FONTES:
   - NÃO liste fontes no corpo do texto
   - NÃO mencione URLs ou links no texto principal
   - As fontes serão adicionadas automaticamente no final

Relatório Integrado (OBRIGATÓRIO: use ## para cada seção):"""

    context = "".join(context_parts) + instructions

    try:
        llm = _get_llm()
        response = llm.invoke(context)
        report_body = response.content.strip()
        
        # Extract sources section only if news were included
        sources_section = ""
        if include_news and news:
            sources = []
            for article in news:
                title = article.get('title', 'Sem título')
                url = article.get('url', '')
                if url:
                    # Clean title - remove extra whitespace and ensure proper formatting
                    clean_title = " ".join(title.split())
                    sources.append(f"[{clean_title}]({url})")
            
            if sources:
                # Format as list, not comma-separated
                sources_list = "\n".join(f"- {source}" for source in sources)
                sources_section = f"\n\n## Fontes\n\n{sources_list}\n"
        
        return report_body, sources_section
    except Exception as e:
        # Fallback - only use confirmed components, with proper markdown
        fallback_parts = ["## Visão Geral\n", f"Análise dos dados SRAG para {location}."]
        
        if include_metrics:
            case_rate = metrics.get("case_increase", {}).get("rate")
            mortality_rate = metrics.get("mortality", {}).get("rate")
            icu_rate = metrics.get("icu_occupancy", {}).get("occupancy_rate")
            fallback_parts.append(
                f"\n\n## Análise das Métricas\n\n"
                f"Os dados indicam uma taxa de aumento de casos de **{case_rate}%**, "
                f"taxa de mortalidade de **{mortality_rate}%**, e ocupação de UTI de **{icu_rate}%**."
            )
        
        fallback_parts.append("\n\n## Implicações e Recomendações\n\nA situação requer monitoramento contínuo.")
        fallback = "\n".join(fallback_parts)
        
        sources_section = ""
        if include_news and news:
            sources = []
            for article in news:
                title = article.get('title', 'Sem título')
                url = article.get('url', '')
                if url:
                    clean_title = " ".join(title.split())
                    sources.append(f"[{clean_title}]({url})")
            if sources:
                sources_list = "\n".join(f"- {source}" for source in sources)
                sources_section = f"\n\n## Fontes\n\n{sources_list}\n"
        
        return fallback, sources_section


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


def render_integrated_report(
    location: str,
    report_body: str,
    charts_section: str,
    sources_section: str,
    include_charts: bool = True,
) -> str:
    """
    Render integrated report with seamless narrative.
    
    Args:
        location: Location description
        report_body: Integrated narrative text
        charts_section: Charts description section (only if include_charts=True)
        sources_section: Sources section (only if news were included)
        include_charts: Whether charts were confirmed for inclusion
    
    Returns:
        Complete report as Markdown string
    """
    template_str = """# Relatório SRAG — {{ location }}
**Gerado em:** {{ generation_date }}

{{ report_body }}

{% if include_charts and charts_section %}
{{ charts_section }}

{% endif %}
{{ sources_section }}

---

**Fonte de Dados:** OpenDATASUS SRAG Dataset (2023-2025)
*Gerado automaticamente pelo Agente SRAG com análises contextualizadas.*
"""

    template = Template(template_str)
    generation_date = datetime.now().strftime("%d/%m/%Y %H:%M")

    return template.render(
        location=location,
        generation_date=generation_date,
        report_body=report_body,
        charts_section=charts_section,
        sources_section=sources_section,
        include_charts=include_charts,
    )


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
    Render report using Jinja2 template (legacy method - kept for backward compatibility).

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


def _extract_location_from_report(lines: list[str]) -> str | None:
    """Extract location from report header."""
    for line in lines:
        if "Relatório SRAG" in line and "—" in line:
            return line.split("—")[-1].strip()
    return None


def _extract_executive_summary(lines: list[str]) -> str | None:
    """Extract executive summary text from report."""
    in_summary = False
    summary_text = []
    for line in lines:
        if "## Resumo Executivo" in line:
            in_summary = True
            continue
        if in_summary and line.strip() and not line.startswith("#"):
            summary_text.append(line.strip())
        elif in_summary and line.startswith("#"):
            break
    return " ".join(summary_text) if summary_text else None


def _extract_metrics_from_report(lines: list[str]) -> dict[str, str]:
    """Extract key metrics from report content."""
    metrics = {}
    in_metrics = False

    for line in lines:
        if "## Métricas" in line or "Métricas Principais" in line:
            in_metrics = True
            continue
        if in_metrics and line.startswith("#"):
            break
        if in_metrics and "|" in line and "---" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2 and parts[0] not in ["Métrica", "Metric"]:
                metrics[parts[0]] = parts[1]

    return metrics


def _format_metric_value(value: str) -> str:
    """Format metric value to 1 decimal place if it's a percentage."""
    if not value or value == "N/A":
        return value

    import re
    # Find all numbers with decimals and format to 1 decimal place
    def format_number(match: re.Match) -> str:
        num = float(match.group())
        return f"{num:.1f}"

    # Match numbers with more than 1 decimal place
    return re.sub(r"-?\d+\.\d{2,}", format_number, value)


def generate_report_summary(report_content: str) -> str:
    """
    Generate formatted markdown summary from integrated report content for chat display.

    Args:
        report_content: Full markdown report content

    Returns:
        Formatted markdown summary for chat display (in Portuguese)

    """
    lines = report_content.split("\n")

    # Extract location
    location = _extract_location_from_report(lines)

    # Extract report body (everything before charts section or sources)
    report_body_lines = []
    for line in lines:
        # Stop at charts section, sources section, or footer
        if (line.strip().startswith("##") and 
            ("Gráfico" in line or "Visualizações" in line or "Fontes" in line)):
            break
        if line.strip().startswith("---"):
            break
        # Skip header lines
        if line.strip() and not line.startswith("#") and not line.startswith("**Gerado"):
            report_body_lines.append(line.strip())

    report_body = " ".join(report_body_lines)

    # Create formatted summary
    summary_parts = []

    # Header
    if location:
        summary_parts.append(f"## Relatório SRAG: {location}")
    else:
        summary_parts.append("## Relatório SRAG")

    summary_parts.append("")

    # Extract first 2-3 paragraphs for summary (limit to ~600 chars)
    if report_body:
        # Split by double newlines or periods
        paragraphs = [p.strip() for p in report_body.split("\n\n") if p.strip()]
        if not paragraphs:
            # Try splitting by sentences
            sentences = [s.strip() + "." for s in report_body.split(". ") if s.strip()]
            # Group sentences into paragraphs
            paragraphs = []
            current_para = []
            for sent in sentences:
                current_para.append(sent)
                if len(" ".join(current_para)) > 150:  # Rough paragraph size
                    paragraphs.append(" ".join(current_para))
                    current_para = []
            if current_para:
                paragraphs.append(" ".join(current_para))

        summary_text = ""
        char_count = 0
        for para in paragraphs[:3]:
            if char_count + len(para) > 600:
                break
            if summary_text:
                summary_text += "\n\n"
            summary_text += para
            char_count += len(para)

        if summary_text:
            summary_parts.append(summary_text)
            summary_parts.append("")

    # Add note about full report
    summary_parts.append("*Relatório completo disponível para download abaixo.*")

    # Fallback if no content extracted
    if len(summary_parts) <= 2:
        return "## Relatório SRAG\n\nRelatório gerado com análises integradas de métricas, gráficos e notícias.\n\n*Relatório completo disponível para download abaixo.*"

    return "\n".join(summary_parts)


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

    # Generate filename: sanitize location name for better readability
    # Simplify "Brasil (nacional)" to just "Brasil"
    location_clean = location
    if "Brasil" in location and "nacional" in location.lower():
        location_clean = "Brasil"
    
    location_safe = (
        location_clean.replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "_")
    )
    # Use only date (not time) for cleaner filenames
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"Relatorio_SRAG_{location_safe}_{date_str}.md"
    file_path = output_dir / filename

    # Save file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return file_path


def save_report_with_images_to_zip(
    report_content: str,
    location: str,
    image_files: dict[str, Path],
    output_dir: Path | None = None,
) -> Path:
    """
    Save report and images to a zip file for download.

    Args:
        report_content: Markdown report content
        location: Location name (for filename)
        image_files: Dictionary mapping image names to file paths (e.g., {"grafico_1.png": Path(...)})
        output_dir: Directory to save zip file (default: reports/ in project root)

    Returns:
        Path to saved zip file
    """
    if output_dir is None:
        project_root = Path(__file__).resolve().parent.parent.parent
        output_dir = project_root / "reports"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    location_clean = location
    if "Brasil" in location and "nacional" in location.lower():
        location_clean = "Brasil"

    location_safe = (
        location_clean.replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "_")
    )
    date_str = datetime.now().strftime("%Y-%m-%d")
    zip_filename = f"Relatorio_SRAG_{location_safe}_{date_str}.zip"
    zip_path = output_dir / zip_filename

    # Create zip file
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add markdown file
        md_filename = f"Relatorio_SRAG_{location_safe}_{date_str}.md"
        zipf.writestr(md_filename, report_content, compress_type=zipfile.ZIP_DEFLATED)

        # Add image files
        for image_name, image_path in image_files.items():
            if image_path.exists():
                zipf.write(image_path, image_name)

    return zip_path
