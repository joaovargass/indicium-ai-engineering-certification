"""Configuration constants for SRAG data processing."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# Path Configuration
# =============================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_PATH = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cleaned"
RAW_DATA_DIR = DATA_DIR / "raw"
TEMP_DIR = RAW_DATA_DIR / "temp"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_IMG_DIR = REPORTS_DIR / "img"
ASSETS_DIR = PROJECT_ROOT / "assets"
ELT_STATUS_CACHE_DIR = PROJECT_ROOT / ".cache" / "elt_status"
BACKGROUND_CALLBACKS_CACHE_DIR = PROJECT_ROOT / ".cache" / "background_callbacks"
CITY_MAPPING_PATH = CACHE_DIR / "city_mapping.json"
ICU_BEDS_CACHE_PATH = CACHE_DIR / "icu_beds_cache.json"
DASH_CACHE_PATH = CACHE_DIR / "dash_cache.parquet"

# =============================================================================
# Timeout Configuration (in seconds)
# =============================================================================
# Base timeout for long operations
LONG_TIMEOUT_SECONDS = 600  # 10 minutes

ELT_STATUS_TIMEOUT_SECONDS = LONG_TIMEOUT_SECONDS
REQUEST_TIMEOUT_SECONDS = LONG_TIMEOUT_SECONDS
CONNECTION_TIMEOUT_SECONDS = LONG_TIMEOUT_SECONDS
READ_TIMEOUT_SECONDS = LONG_TIMEOUT_SECONDS

# Shorter timeouts for specific operations
REQUEST_HEAD_TIMEOUT_SECONDS = 30
LOCATION_REQUEST_TIMEOUT_SECONDS = 30
ICU_BEDS_REQUEST_TIMEOUT_SECONDS = 120

# =============================================================================
# Cache Configuration
# =============================================================================
ICU_BEDS_CACHE_TTL_DAYS = 7

# =============================================================================
# ICU Beds Configuration
# =============================================================================
# Fallback static data (Dec 2024) - used if CNES API unavailable
FALLBACK_ICU_BEDS = {
    "SP": 15695,
    "RJ": 8456,
    "MG": 5894,
    "PR": 3731,
    "BA": 3299,
    "RS": 2996,
    "PE": 2917,
    "GO": 2156,
    "DF": 2089,
    "SC": 1942,
    "CE": 1833,
    "ES": 1724,
    "PA": 1622,
    "MA": 1234,
    "MT": 1185,
    "PB": 1009,
    "RN": 834,
    "AM": 808,
    "MS": 761,
    "AL": 697,
    "RO": 640,
    "PI": 564,
    "SE": 491,
    "TO": 428,
    "AP": 185,
    "AC": 106,
    "RR": 105,
}
FALLBACK_BRAZIL_TOTAL = 63401

# Mapping from IBGE state code (first 2 digits) to UF
IBGE_STATE_TO_UF = {
    "11": "RO",
    "12": "AC",
    "13": "AM",
    "14": "RR",
    "15": "PA",
    "16": "AP",
    "17": "TO",
    "21": "MA",
    "22": "PI",
    "23": "CE",
    "24": "RN",
    "25": "PB",
    "26": "PE",
    "27": "AL",
    "28": "SE",
    "29": "BA",
    "31": "MG",
    "32": "ES",
    "33": "RJ",
    "35": "SP",
    "41": "PR",
    "42": "SC",
    "43": "RS",
    "50": "MS",
    "51": "MT",
    "52": "GO",
    "53": "DF",
}

# =============================================================================
# UI Defaults
# =============================================================================
DEFAULT_PORT = 8050
DEFAULT_HOST = "0.0.0.0"

# UI Intervals (in milliseconds)
LOADING_INTERVAL_MS = 500
ELT_STATUS_CHECK_INTERVAL_MS = 2000
SCROLL_DELAY_MS = 100

# =============================================================================
# Chart Defaults
# =============================================================================
DEFAULT_CHART_WIDTH = 1200
DEFAULT_CHART_HEIGHT = 600
DEFAULT_DAYS = 30
DEFAULT_MONTHS = 12

# Chart styling
CHART_COLOR = "#2E86AB"
CHART_MARGIN = {"l": 60, "r": 40, "t": 80, "b": 60}
CHART_TITLE_FONT_SIZE = 20
CHART_FONT_SIZE = 12
CHART_ANNOTATION_FONT_SIZE = 16
CHART_LINE_WIDTH = 3
CHART_MARKER_SIZE = 7
CHART_BAR_GAP = 0.2

# CSS Class Names
SPINNER_CLASS_VISIBLE = "elt-spinner-active"
SPINNER_CLASS_HIDDEN = "elt-spinner-hidden"

# =============================================================================
# Metrics Defaults
# =============================================================================
DEFAULT_PERIOD_DAYS = 7
DEFAULT_LOOKBACK_DAYS = 30

# =============================================================================
# Report Defaults
# =============================================================================
NEWS_API_MAX_RESULTS = 20

# =============================================================================
# Text Truncation Limits
# =============================================================================
EXPLANATION_MAX_LENGTH = 300
NEWS_SUMMARY_MAX_LENGTH = 200
ARTICLE_PREVIEW_LENGTH = 150
REPORT_SUMMARY_PARAGRAPH_LENGTH = 150
REPORT_SUMMARY_MAX_CHARS = 600
REPORT_CONTENT_PREVIEW_LENGTH = 300

# =============================================================================
# LLM Configuration
# =============================================================================
DEFAULT_MODEL_NAME = "gpt-5-nano"
DEFAULT_TEMPERATURE = 0.0
REPORT_TEMPERATURE = 0.3

# =============================================================================
# Agent Configuration
# =============================================================================
# Tool name to step message mapping for loading indicators
TOOL_STEP_MAPPING = {
    "get_case_increase_rate": "Calculando taxa de aumento de casos...",
    "get_mortality_rate": "Calculando taxa de mortalidade...",
    "get_icu_occupancy_rate": "Calculando taxa de ocupação de UTI...",
    "get_vaccination_rate": "Calculando taxas de vacinação...",
    "get_daily_chart_json": "Gerando gráfico de casos diários...",
    "get_monthly_chart_json": "Gerando gráfico de casos mensais...",
    "generate_download_report": "Gerando relatório completo...",
    "generate_chat_report": "Gerando relatório interativo...",
    "search_srag_news_tool": "Buscando notícias de saúde...",
}

# =============================================================================
# Validation Limits
# =============================================================================
CHART_DAYS_MIN = 7
CHART_DAYS_MAX = 90
CHART_MONTHS_MIN = 1
CHART_MONTHS_MAX = 24

# News limits (used as both default and max)
MAX_NEWS_ARTICLES = 5

# =============================================================================
# Error Messages
# =============================================================================
_NO_DATA_MESSAGE_TEMPLATE = (
    "Dados não disponíveis. Por favor, clique no botão 'Atualizar Dados' "
    "no canto superior direito para carregar os dados do SRAG antes de {action}."
)
NO_DATA_MESSAGE_METRICS = _NO_DATA_MESSAGE_TEMPLATE.format(action="fazer consultas")
NO_DATA_MESSAGE_CHARTS = _NO_DATA_MESSAGE_TEMPLATE.format(action="gerar gráficos")

# =============================================================================
# External API URLs
# =============================================================================
CNES_LEITOS_URL_TEMPLATE = (
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/Leitos_SUS/Leitos_{year}.csv"
)

# =============================================================================
# Execution Flags
# =============================================================================
FULL_REFRESH = False
DOWNLOAD_ENABLED = True

# Azure Storage configuration
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME", "desafioai")
FILE_SYSTEM_NAME = os.getenv("FILE_SYSTEM_NAME", "desafio-ai")

# Azure paths for raw data
RAW_STATE_PATH = "raw/state.json"
RAW_DELTAS_DIR = "raw/deltas"

# Azure paths for DW data
DW_STATE_PATH = "clean/dw_state.json"

# Data source configuration
BASE_DOWNLOAD_URL = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG"
OPENDATASUS_URL = "https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024"

# Start year for data collection
START_YEAR = 2023

# COVID vaccination era start (for data validation)
COVID_VACCINATION_START_DATE = "2021-01-01"

# Primary key field
PRIMARY_KEY_FIELD = "NU_NOTIFIC"

# Fields to exclude from "all null" check
EXCLUDED_FROM_NULL_CHECK = [PRIMARY_KEY_FIELD, "DT_NOTIFIC", "DT_SIN_PRI"]

# Date columns for transformation
DATE_COLUMNS = [
    "DT_NOTIFIC",
    "DT_SIN_PRI",
    "DT_EVOLUCA",
    "DT_INTERNA",
    "DT_ENTUTI",
    "DT_SAIDUTI",
    "DOSE_1_COV",
    "DOSE_2_COV",
    "DOSE_REF",
    "DOSE_ADIC",
]

# Fields where 9 = Ignored (convert to NULL)
IGNORED_FIELDS = ["EVOLUCAO", "UTI", "VACINA_COV", "VACINA", "HOSPITAL"]

# Categorical field validations
CATEGORICAL_VALIDATIONS = {
    "EVOLUCAO": ["1", "2", "3"],
    "UTI": ["1", "2"],
    "VACINA_COV": ["1", "2"],
    "VACINA": ["1", "2"],
    "HOSPITAL": ["1", "2"],
}

# Strings that should be treated as NULL
NULL_STRINGS = ["NULL", "NONE", "N/A", "NA"]

# Essential columns for metrics calculation
ESSENTIAL_COLUMNS = [
    "NU_NOTIFIC",
    "DT_NOTIFIC",
    "DT_SIN_PRI",
    "CO_REGIONA",
    "SG_UF_NOT",
    "CO_MUN_NOT",
    "EVOLUCAO",
    "DT_EVOLUCA",
    "HOSPITAL",
    "UTI",
    "DT_ENTUTI",
    "DT_SAIDUTI",
    "DT_INTERNA",
    "VACINA_COV",
    "VACINA",
    "DOSE_1_COV",
    "DOSE_2_COV",
    "DOSE_REF",
    "DOSE_ADIC",
]

# COVID vaccine date columns
COVID_VACCINE_DATE_COLS = [
    "DOSE_1_COV",
    "DOSE_2_COV",
    "DOSE_REF",
    "DOSE_2REF",
    "DOSE_ADIC",
    "DOS_RE_BI",
]

# Azure Data Warehouse configuration
DW_FULLY_QUALIFIED_TABLE = "dbo.srag_cleaned"
DW_UPLOAD_CHUNK_SIZE = 500000  # Rows per parquet file when uploading to staging

# Brazilian states (UF codes) - All 27 states
BRAZILIAN_STATES = [
    "AC",  # Acre
    "AL",  # Alagoas
    "AP",  # Amapá
    "AM",  # Amazonas
    "BA",  # Bahia
    "CE",  # Ceará
    "DF",  # Distrito Federal
    "ES",  # Espírito Santo
    "GO",  # Goiás
    "MA",  # Maranhão
    "MT",  # Mato Grosso
    "MS",  # Mato Grosso do Sul
    "MG",  # Minas Gerais
    "PA",  # Pará
    "PB",  # Paraíba
    "PR",  # Paraná
    "PE",  # Pernambuco
    "PI",  # Piauí
    "RJ",  # Rio de Janeiro
    "RN",  # Rio Grande do Norte
    "RS",  # Rio Grande do Sul
    "RO",  # Rondônia
    "RR",  # Roraima
    "SC",  # Santa Catarina
    "SP",  # São Paulo
    "SE",  # Sergipe
    "TO",  # Tocantins
]

# Brazilian state full names (lowercase for pattern matching)
STATE_NAME_PATTERNS = [
    "são paulo",
    "rio de janeiro",
    "rio grande do sul",
    "minas gerais",
    "santa catarina",
    "paraná",
    "bahia",
    "goiás",
    "ceará",
    "pernambuco",
    "pará",
    "amazonas",
    "espírito santo",
    "mato grosso",
    "rio grande do norte",
    "alagoas",
    "piauí",
    "maranhão",
    "paraíba",
    "distrito federal",
    "rondônia",
    "acre",
    "amapá",
    "roraima",
    "sergipe",
    "tocantins",
    "mato grosso do sul",
]

# Health-related keywords for news search enhancement (Portuguese)
HEALTH_KEYWORDS_PT = [
    "saúde",
    "SRAG",
    "gripe",
    "influenza",
    "surto",
    "epidemia",
    "pandemia",
    "casos",
    "mortes",
    "óbitos",
    "hospitalização",
    "internação",
    "UTI",
    "unidade de terapia intensiva",
    "vacinação",
    "vacina",
    "COVID-19",
    "COVID",
    "coronavírus",
    "síndrome respiratória",
    "doença respiratória",
    "vírus respiratório",
    "gripe aviária",
    "H5N1",
    "H1N1",
    "notificação",
    "vigilância epidemiológica",
    "Ministério da Saúde",
    "DATASUS",
]

# Health-related keywords for news search enhancement (English)
HEALTH_KEYWORDS_EN = [
    "health",
    "outbreak",
    "epidemic",
    "pandemic",
    "cases",
    "deaths",
    "hospitalization",
    "ICU",
    "intensive care",
    "vaccination",
    "vaccine",
    "COVID-19",
    "coronavirus",
    "respiratory syndrome",
    "respiratory disease",
    "respiratory virus",
    "avian flu",
    "H5N1",
    "H1N1",
    "epidemiological surveillance",
]
