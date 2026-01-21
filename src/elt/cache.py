"""Cache and data loading for SRAG data."""

import pandas as pd

from common.config import CACHE_DIR, DASH_CACHE_PATH
from common.logging import logger
from elt.dw import read_from_dw


class NoDataAvailableError(Exception):
    """Raised when no SRAG data is available."""

    pass


def load_srag_data() -> pd.DataFrame:
    """Load SRAG data from cache or DW. Raises NoDataAvailableError if unavailable or empty."""
    if DASH_CACHE_PATH.exists():
        df = pd.read_parquet(DASH_CACHE_PATH)
        if df.empty:
            raise NoDataAvailableError(
                "O cache de dados está vazio. Use o botão 'Atualizar Dados' para carregar os dados."
            )
        return df

    try:
        df = read_from_dw()
    except Exception as e:
        logger.warning("Failed to load SRAG from DW: %s", e)
        raise NoDataAvailableError(
            "Dados não disponíveis. Use o botão 'Atualizar Dados' para carregar os dados do SRAG."
        ) from e

    if df.empty:
        raise NoDataAvailableError(
            "Nenhum dado encontrado no Data Warehouse. Use o botão 'Atualizar Dados' para carregar os dados."
        )

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(DASH_CACHE_PATH, index=False)

    return df
