import pandas as pd

RAW_KEY_COLUMNS = ["date", "state", "commodity", "market"]


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset=RAW_KEY_COLUMNS, keep="first")
    dropped = before - len(df)
    if dropped:
        print(f"Dropped {dropped} exact-duplicate rows on {RAW_KEY_COLUMNS}")
    return df


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
    return df


def coerce_price(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["price"] = pd.to_numeric(df["price"], errors="raise")
    return df


def flag_price_outliers(df: pd.DataFrame, k: float = 3.0) -> pd.DataFrame:
    """Flag (never drop) statistical outliers per commodity+market group via Tukey's fences.

    k=3.0 (rather than the usual 1.5) deliberately errs toward under-flagging: real
    commodity prices swing hard during genuine supply shocks (e.g. onion crises), and
    those swings are signal for the secondary hypotheses, not noise to be removed.
    """
    df = df.copy()
    flags = pd.Series(False, index=df.index)
    for _, group in df.groupby(["commodity", "market"]):
        prices = group["price"]
        q1, q3 = prices.quantile([0.25, 0.75])
        iqr = q3 - q1
        lo, hi = q1 - k * iqr, q3 + k * iqr
        flags.loc[group.index] = (prices < lo) | (prices > hi)
    df["price_outlier"] = flags.fillna(False)
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Type-coerce, dedup, and flag outliers.

    Missing prices are kept as NaN and flagged via `price_missing`, never dropped or
    imputed: dropping rows would silently change which states/commodities remain in
    the panel, and imputing would fabricate values for a rigor-focused analysis.
    """
    df = df.drop(columns=["note"])
    df = deduplicate(df)
    df = parse_dates(df)
    df = coerce_price(df)
    df["price_missing"] = df["price"].isna()
    df = flag_price_outliers(df)
    return df
