import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

TICKERS = {
    "Vale": "VALE3.SA",
    "Itaú": "ITUB4.SA",
    "Petrobras": "PETR4.SA",
}

_cache = {"data": None, "timestamp": None}
CACHE_TTL = 1800  # 30 minutos


def get_data():
    now = time.time()
    if _cache["data"] is not None and (now - _cache["timestamp"]) < CACHE_TTL:
        return _cache["data"]

    raw = yf.download(
        list(TICKERS.values()),
        start="2026-01-01",
        end=datetime.today().strftime("%Y-%m-%d"),
        auto_adjust=True,
        progress=False,
    )

    close = raw["Close"].copy()
    close.columns = list(TICKERS.keys())
    close = close.dropna(how="all")

    volume = raw["Volume"].copy()
    volume.columns = list(TICKERS.keys())
    volume = volume.dropna(how="all")

    result = {"close": close, "volume": volume}
    _cache["data"] = result
    _cache["timestamp"] = now
    return result


def get_summary(close_df):
    summary = {}
    for name in close_df.columns:
        series = close_df[name].dropna()
        if series.empty:
            continue
        first = series.iloc[0]
        last = series.iloc[-1]
        summary[name] = {
            "preco_atual": round(last, 2),
            "variacao_ano": round((last / first - 1) * 100, 2),
            "maximo": round(series.max(), 2),
            "minimo": round(series.min(), 2),
        }
    return summary
