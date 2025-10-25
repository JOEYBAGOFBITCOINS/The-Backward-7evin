"""Demo version using sample data"""
import pandas as pd
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()

# Load sample data
df = pd.read_csv('data/market_history_sample.csv', parse_dates=['Date'], index_col='Date')
df = df.dropna()

console.print(Panel.fit(
    Text("THE BACKWARD 7EVIN", justify="center", style="bold magenta"),
    subtitle="Cryptocurrency Correlation Intelligence (Demo with Sample Data)",
    border_style="magenta",
    padding=(1, 4),
))

console.print(f"\n[bold cyan]Loaded {len(df)} days of historical data[/bold cyan]")
console.print(f"Date range: {df.index.min().date()} to {df.index.max().date()}\n")

# Calculate correlations with Bitcoin
btc_corrs = {}
for col in df.columns:
    if col != 'BTC-USD' and df[col].notna().sum() > 10:
        corr = df['BTC-USD'].corr(df[col])
        if not np.isnan(corr):
            btc_corrs[col.replace('-USD', '')] = corr

# Create results table
table = Table(title="Cryptocurrency Correlation with Bitcoin", header_style="bold cyan", box=box.ROUNDED)
table.add_column("Asset", style="bold white")
table.add_column("BTC Correlation", justify="right")
table.add_column("Signal", justify="center")

for asset, corr in sorted(btc_corrs.items(), key=lambda x: abs(x[1]), reverse=True):
    if corr > 0.7:
        signal = "🟢 Strong Positive"
        style = "bold green"
    elif corr > 0.3:
        signal = "🟡 Moderate Positive"
        style = "yellow"
    elif corr < -0.3:
        signal = "🔴 Negative"
        style = "bold red"
    else:
        signal = "⚪ Weak/Neutral"
        style = "white"
    
    table.add_row(asset, f"{corr:+.3f}", Text(signal, style=style))

console.print(table)
console.print(f"\n[bold green]✓ Analysis complete![/bold green]\n")
