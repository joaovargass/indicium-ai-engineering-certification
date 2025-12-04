"""Configuration constants for SRAG data processing."""

# Execution flags
FULL_REFRESH = False
RESET = False
DOWNLOAD_ENABLED = True

# Azure Storage configuration
STORAGE_ACCOUNT_NAME = "desafioai"
FILE_SYSTEM_NAME = "desafio-ai"

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
