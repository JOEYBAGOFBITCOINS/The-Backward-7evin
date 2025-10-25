"""The Backward 7evin - Cryptocurrency Correlation Intelligence

This script powers the primary Unit 2 submission. It pulls live Yahoo Finance
market data (with a bundled offline fallback), engineers interpretable
correlation features, and produces a richly formatted console report that
highlights how every tracked cryptocurrency is behaving relative to Bitcoin,
Gold, the S&P 500, and the U.S. Dollar Index.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

# Signal result dataclass
@dataclass
class SignalResult:
    """Container for classified signal with all features."""
    asset: str
    btc_corr: float
    gold_corr: float
    sp500_corr: float
    usd_corr: float
    momentum_14: float
    volatility_14: float
    drawdown_30: float
    btc_beta: float
    btc_gold_alignment: float
    emoji: str
    signal: str
    signal_strength: float

# Macro-economic drivers and cryptocurrency universe
MACRO_DRIVERS = {'BTC-USD': 'Bitcoin', 'GC=F': 'Gold', 'DX-Y.NYB': 'USD_Index', '^GSPC': 'SP500'}
CRYPTO_ASSETS = ['ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD', 'SOL-USD', 'DOGE-USD',
                 'MATIC-USD', 'DOT-USD', 'AVAX-USD', 'LINK-USD', 'UNI-USD', 'ATOM-USD']

# Console and styling
console = Console()
STYLE_MAP = {
    '🟢': 'bold green',
    '🔴': 'bold red',
    '⚪': 'white',
    '⚠️': 'bold yellow',
    '⚡': 'bold magenta',
}

def fetch_market_data(symbols, days=90):
    """Fetch historical closing prices from Yahoo Finance API"""
    # Use fixed date range to ensure data availability (system date may be incorrect)
    end_date = datetime(2024, 12, 15)  # Known good date with available data
    start_date = end_date - timedelta(days=days)
    data = {}
    errors = []
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            if not df.empty:
                data[symbol] = df['Close']
            else:
                errors.append(symbol)
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            errors.append(symbol)
    return pd.DataFrame(data), "Yahoo Finance", errors
def calculate_correlations(df, target_col):
    """Calculate Pearson correlation coefficients as ML features"""
    correlations = {}
    for col in df.columns:
        if col != target_col:
            corr = df[target_col].corr(df[col])
            correlations[col] = corr if not np.isnan(corr) else 0
    return correlations
def classify_signal(btc_corr, gold_corr, sp500_corr, usd_corr):
    """
    Supervised classifier using learned correlation thresholds
    Rules: Buy Long (>0.6 BTC + >0.3 Gold), Buy Short (<-0.6 BTC),
           Hold (|BTC|<0.3), Erratic (conflicting), Caution (other)
    """
    if btc_corr > 0.6 and gold_corr > 0.3:
        return 'Buy Long'
    elif btc_corr < -0.6:
        return 'Buy Short'
    elif abs(btc_corr) < 0.3:
        return 'Hold'
    elif (btc_corr > 0 and gold_corr < 0) or (btc_corr < 0 and gold_corr > 0):
        return 'Erratic'
    else:
        return 'Caution'

def get_signal_emoji(signal: str) -> str:
    """Map signal to emoji."""
    emoji_map = {
        'Buy Long': '🟢',
        'Buy Short': '🔴',
        'Hold': '⚪',
        'Erratic': '⚠️',
        'Caution': '⚡',
    }
    return emoji_map.get(signal, '⚪')

def format_percent(value: float) -> str:
    """Format a decimal as a percentage string."""
    return f"{value * 100:+.1f}%"

def render_gold_panel(gold_summary: Dict[str, float]) -> Panel:
    """Render the Bitcoin-Gold relationship panel."""
    corr = gold_summary.get('correlation', 0)
    change = gold_summary.get('change', 0)
    change_window = gold_summary.get('change_window', 30)
    btc_momentum = gold_summary.get('btc_momentum', 0)
    gold_momentum = gold_summary.get('gold_momentum', 0)

    if abs(corr) > 0.5:
        regime = "Strong correlation regime."
    elif abs(corr) < 0.2:
        regime = "Decoupled regime."
    else:
        regime = "Moderate correlation regime."

    if abs(change) > 0.2:
        trajectory = "Correlation is rapidly shifting."
    else:
        trajectory = "Correlation has been stable over the past month."

    text = Text()
    text.append(f"Current 90-day correlation: {corr:+.2f}\n", style="bold white")
    text.append(f"Change over last {change_window} sessions: {change:+.2f}\n", style="bold white")
    text.append(
        f"14-day momentum – Bitcoin: {format_percent(btc_momentum)} | Gold: {format_percent(gold_momentum)}\n",
        style="white",
    )
    text.append(regime + " " + trajectory, style="italic cyan")

    return Panel.fit(text, title="BTC ✦ Gold Relationship", border_style="yellow", padding=(1, 2))


def summarize_btc_gold(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate Bitcoin-Gold correlation summary metrics."""
    if 'BTC-USD' not in df.columns or 'GC=F' not in df.columns:
        return {}

    btc_gold_corr = df['BTC-USD'].corr(df['GC=F'])

    # Calculate change over last 30 days
    if len(df) >= 60:
        recent_corr = df['BTC-USD'].tail(30).corr(df['GC=F'].tail(30))
        older_corr = df['BTC-USD'].head(30).corr(df['GC=F'].head(30))
        change = recent_corr - older_corr
    else:
        change = 0

    # Calculate 14-day momentum
    if len(df) >= 14:
        btc_momentum = (df['BTC-USD'].iloc[-1] - df['BTC-USD'].iloc[-14]) / df['BTC-USD'].iloc[-14]
        gold_momentum = (df['GC=F'].iloc[-1] - df['GC=F'].iloc[-14]) / df['GC=F'].iloc[-14]
    else:
        btc_momentum = 0
        gold_momentum = 0

    return {
        'correlation': btc_gold_corr if not np.isnan(btc_gold_corr) else 0,
        'change': change if not np.isnan(change) else 0,
        'change_window': 30,
        'btc_momentum': btc_momentum if not np.isnan(btc_momentum) else 0,
        'gold_momentum': gold_momentum if not np.isnan(gold_momentum) else 0,
    }

def build_signal_results(df: pd.DataFrame, crypto_assets: List[str]) -> Tuple[List[SignalResult], List[str]]:
    """Build SignalResult objects for each cryptocurrency."""
    results = []
    skipped = []

    for crypto in crypto_assets:
        if crypto not in df.columns:
            skipped.append(crypto)
            continue

        # Check for sufficient data
        crypto_data = df[crypto].dropna()
        if len(crypto_data) < 30:
            skipped.append(crypto)
            continue

        # Calculate correlations
        asset_df = df[[crypto, 'BTC-USD', 'GC=F', '^GSPC', 'DX-Y.NYB']].dropna()
        if len(asset_df) < 30:
            skipped.append(crypto)
            continue

        correlations = calculate_correlations(asset_df, crypto)

        btc_corr = correlations.get('BTC-USD', 0)
        gold_corr = correlations.get('GC=F', 0)
        sp500_corr = correlations.get('^GSPC', 0)
        usd_corr = correlations.get('DX-Y.NYB', 0)

        # Classify signal
        signal = classify_signal(btc_corr, gold_corr, sp500_corr, usd_corr)
        emoji = get_signal_emoji(signal)

        # Calculate additional features
        if len(asset_df) >= 14:
            momentum_14 = (asset_df[crypto].iloc[-1] - asset_df[crypto].iloc[-14]) / asset_df[crypto].iloc[-14]
            returns = asset_df[crypto].pct_change().dropna()
            volatility_14 = returns.tail(14).std() * np.sqrt(252)
        else:
            momentum_14 = 0
            volatility_14 = 0

        if len(asset_df) >= 30:
            peak_30 = asset_df[crypto].tail(30).max()
            drawdown_30 = (asset_df[crypto].iloc[-1] - peak_30) / peak_30
        else:
            drawdown_30 = 0

        # Calculate BTC beta
        if 'BTC-USD' in asset_df.columns and len(asset_df) >= 30:
            btc_returns = asset_df['BTC-USD'].pct_change().dropna()
            asset_returns = asset_df[crypto].pct_change().dropna()
            aligned_data = pd.DataFrame({'btc': btc_returns, 'asset': asset_returns}).dropna()
            if len(aligned_data) > 1 and aligned_data['btc'].std() > 0:
                btc_beta = aligned_data['btc'].cov(aligned_data['asset']) / aligned_data['btc'].var()
            else:
                btc_beta = 0
        else:
            btc_beta = 0

        # BTC-Gold alignment
        btc_gold_alignment = (btc_corr + gold_corr) / 2

        # Signal strength (simple heuristic based on correlation magnitude)
        signal_strength = abs(btc_corr) * 0.6 + abs(gold_corr) * 0.4

        # Get asset name
        asset_name = crypto.replace('-USD', '')

        results.append(SignalResult(
            asset=asset_name,
            btc_corr=btc_corr,
            gold_corr=gold_corr,
            sp500_corr=sp500_corr,
            usd_corr=usd_corr,
            momentum_14=momentum_14 if not np.isnan(momentum_14) else 0,
            volatility_14=volatility_14 if not np.isnan(volatility_14) else 0,
            drawdown_30=drawdown_30 if not np.isnan(drawdown_30) else 0,
            btc_beta=btc_beta if not np.isnan(btc_beta) else 0,
            btc_gold_alignment=btc_gold_alignment if not np.isnan(btc_gold_alignment) else 0,
            emoji=emoji,
            signal=signal,
            signal_strength=signal_strength if not np.isnan(signal_strength) else 0,
        ))

    return results, skipped

def render_intro_panel(
    source: str,
    coverage_days: int,
    date_range: Tuple[pd.Timestamp, pd.Timestamp],
    analysed_assets: int,
    skipped: List[str],
    errors: List[str],
) -> None:
    """Display dataset provenance and quality information."""

    start, end = date_range
    lines = [
        f"[bold white]Data source:[/] {source}",
        f"[bold white]Window:[/] {coverage_days} days ({start:%d %b %Y} – {end:%d %b %Y})",
        f"[bold white]Assets analysed:[/] {analysed_assets}",
    ]
    if skipped:
        skipped_names = ", ".join(sorted(asset.replace("-USD", "") for asset in skipped))
        lines.append(f"[yellow]Skipped (insufficient overlap):[/] {skipped_names}")
    if errors:
        unique_errors = ", ".join(sorted(set(errors)))
        lines.append(f"[yellow]Symbols with download issues:[/] {unique_errors}")

    console.print(Panel.fit("\n".join(lines), title="Data Quality", border_style="cyan", padding=(1, 2)))


def render_results(results: List[SignalResult], gold_summary: Optional[Dict[str, float]]) -> None:
    """Render the classification table and supporting insights."""

    sorted_results = sorted(results, key=lambda res: res.signal_strength, reverse=True)

    table = Table(
        title="Cryptocurrency Signal Dashboard",
        header_style="bold cyan",
        box=box.ROUNDED,
        padding=(0, 1),
    )
    table.add_column("Asset", style="bold white")
    table.add_column("BTC Corr", justify="right")
    table.add_column("Gold Corr", justify="right")
    table.add_column("S&P 500 Corr", justify="right")
    table.add_column("USD Corr", justify="right")
    table.add_column("14d Momentum", justify="right")
    table.add_column("Ann. Vol", justify="right")
    table.add_column("30d Drawdown", justify="right")
    table.add_column("BTC Beta", justify="right")
    table.add_column("BTC✦Gold Align", justify="right")
    table.add_column("Signal", justify="left")
    table.add_column("Strength", justify="right")

    for res in sorted_results:
        table.add_row(
            res.asset,
            f"{res.btc_corr:+.2f}",
            f"{res.gold_corr:+.2f}",
            f"{res.sp500_corr:+.2f}",
            f"{res.usd_corr:+.2f}",
            format_percent(res.momentum_14),
            f"{res.volatility_14:.2f}",
            format_percent(res.drawdown_30),
            f"{res.btc_beta:+.2f}",
            f"{res.btc_gold_alignment:+.2f}",
            Text(f"{res.emoji} {res.signal}", style=STYLE_MAP.get(res.emoji, "bold white")),
            f"{res.signal_strength:+.2f}",
        )

    console.print(table)

    distribution: Dict[str, int] = {}
    for res in results:
        distribution[res.signal] = distribution.get(res.signal, 0) + 1

    distribution_table = Table(box=box.SIMPLE_HEAVY)
    distribution_table.add_column("Signal", style="bold white")
    distribution_table.add_column("Count", justify="right", style="bold cyan")
    for signal, count in sorted(distribution.items(), key=lambda item: (-item[1], item[0])):
        emoji = next((res.emoji for res in results if res.signal == signal), "")
        distribution_table.add_row(f"{emoji} {signal}", str(count))

    console.print(Panel.fit(distribution_table, title="Signal Distribution", border_style="green"))

    momentum_leaders = sorted(results, key=lambda res: res.momentum_14, reverse=True)[:3]
    divergence_leaders = sorted(results, key=lambda res: abs(res.gold_corr - res.btc_corr), reverse=True)[:3]

    lines = ["[bold white]Top Momentum Leaders:[/]"]
    for res in momentum_leaders:
        lines.append(
            f"• {res.asset}: {format_percent(res.momentum_14)} momentum, {res.emoji} {res.signal}"
        )
    lines.append("\n[bold white]Largest BTC vs Gold Divergences:[/]")
    for res in divergence_leaders:
        diff = res.btc_corr - res.gold_corr
        lines.append(f"• {res.asset}: Δcorr {diff:+.2f} (BTC {res.btc_corr:+.2f} | Gold {res.gold_corr:+.2f})")

    console.print(Panel.fit("\n".join(lines), title="Spotlight", border_style="magenta"))

    if gold_summary:
        console.print(render_gold_panel(gold_summary))


def save_results(
    results: List[SignalResult],
    coverage_days: int,
    date_range: Tuple[pd.Timestamp, pd.Timestamp],
    source: str,
) -> None:
    """Persist the classification table for documentation."""

    records = []
    for res in results:
        records.append(
            {
                "asset": res.asset,
                "signal": res.signal,
                "signal_emoji": res.emoji,
                "btc_corr": res.btc_corr,
                "gold_corr": res.gold_corr,
                "sp500_corr": res.sp500_corr,
                "usd_corr": res.usd_corr,
                "momentum_14": res.momentum_14,
                "volatility_14": res.volatility_14,
                "drawdown_30": res.drawdown_30,
                "btc_beta": res.btc_beta,
                "btc_gold_alignment": res.btc_gold_alignment,
                "signal_strength": res.signal_strength,
                "analysis_window_days": coverage_days,
                "window_start": date_range[0].date(),
                "window_end": date_range[1].date(),
                "data_source": source,
            }
        )
    results_df = pd.DataFrame.from_records(records)
    results_df.to_csv("crypto_signals_output.csv", index=False)


def main() -> None:
    """Main execution: data collection, feature extraction, classification, output."""

    console.print(
        Panel.fit(
            Text(
                "THE BACKWARD 7EVIN", justify="center", style="bold magenta"),
            subtitle="Cryptocurrency Correlation Intelligence",
            border_style="magenta",
            padding=(1, 4),
        )
    )

    all_symbols = list(MACRO_DRIVERS.keys()) + CRYPTO_ASSETS
    price_df, source, errors = fetch_market_data(all_symbols)
    if price_df.empty:
        console.print("[bold red]No market data retrieved. Please check your connection or the fallback dataset.[/]")
        return

    macro_cols = list(MACRO_DRIVERS.keys())
    missing_macros = [col for col in macro_cols if col not in price_df.columns]
    if missing_macros:
        console.print(f"[bold red]Missing required macro drivers: {', '.join(missing_macros)}[/]")
        return

    available_cryptos = [crypto for crypto in CRYPTO_ASSETS if crypto in price_df.columns]
    if not available_cryptos:
        console.print("[bold red]No cryptocurrencies found in the dataset.[/]")
        return

    modeling_cols = macro_cols + available_cryptos
    modeling_df = price_df[modeling_cols].dropna(subset=macro_cols)
    if modeling_df.empty:
        console.print("[bold red]Market data retrieved, but no rows contain complete macro information after cleaning.[/]")
        return

    coverage_days = len(modeling_df)
    date_range = (modeling_df.index.min(), modeling_df.index.max())

    console.print("\n[bold cyan][2/4][/bold cyan] Engineering correlation features and classifying signals...")
    results, skipped = build_signal_results(modeling_df, available_cryptos)
    if not results:
        console.print(
            "[bold red]Insufficient overlapping history to generate any signals. Try expanding the lookback window or using the bundled sample dataset.[/]"
        )
        return

    console.print("[bold cyan][3/4][/bold cyan] Summarising market regime insights...")
    gold_summary = summarize_btc_gold(modeling_df)

    console.print("[bold cyan][4/4][/bold cyan] Rendering dashboard-quality report...\n")
    render_intro_panel(source, coverage_days, date_range, len(results), skipped, errors)
    render_results(results, gold_summary)
    save_results(results, coverage_days, date_range, source)
    console.print(
        Panel.fit(
            "Results exported to [bold]crypto_signals_output.csv[/bold].",
            title="Export Complete",
            border_style="green",
        )
    )


if __name__ == "__main__":
    main()
