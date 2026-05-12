"""Cached dataset fetcher used by all bootcamp notebooks.

Usage:
    from shared.data_utils import load_dataset
    df = load_dataset("penguins")
"""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

CACHE_DIR = Path.home() / ".cache" / "ai-bootcamp"

DATASETS: dict[str, str] = {
    "penguins": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv",
    "titanic": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv",
    "tips": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv",
    "iris": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv",
    # AAPL daily closing prices (2014). The Grand Finale lab injects synthetic
    # NaNs into this so students get to practice cleaning real-shaped data.
    "stock-prices": "https://raw.githubusercontent.com/plotly/datasets/master/2014_apple_stock.csv",
}


def load_dataset(name: str, force_refresh: bool = False) -> pd.DataFrame:
    """Fetch a named dataset, caching it locally on first use."""
    if name not in DATASETS:
        raise KeyError(
            f"Unknown dataset {name!r}. Available: {sorted(DATASETS)}"
        )

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{name}.csv"

    if force_refresh or not cache_file.exists():
        url = DATASETS[name]
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        cache_file.write_bytes(resp.content)

    return pd.read_csv(cache_file)


def list_datasets() -> list[str]:
    return sorted(DATASETS)
