"""UI constants for the chat interface."""

# Welcome message displayed when chat starts
WELCOME_MESSAGE = (
    "Olá! Sou seu assistente de dados SRAG. Posso ajudá-lo com:\n"
    "- Consultar métricas (taxas de mortalidade, ocupação de UTI, taxas de vacinação)\n"
    "- Gerar gráficos e visualizações\n"
    "- Criar relatórios completos\n"
    "- Buscar notícias relevantes sobre saúde\n\n"
    "Como posso ajudar?"
)

# Chart tool names for identifying chart-related tool calls
CHART_TOOL_NAMES = frozenset({"get_daily_chart_json", "get_monthly_chart_json"})

# Loading indicator messages
LOADING_DEFAULT_MESSAGE = "Pensando..."
LOADING_PROCESSING_MESSAGE = "Processando resultados..."

# CSS class constants for loading visibility
LOADING_VISIBLE_CLASS = "loading-indicator-overlay loading-indicator-visible"
LOADING_HIDDEN_CLASS = "loading-indicator-overlay loading-indicator-hidden"
