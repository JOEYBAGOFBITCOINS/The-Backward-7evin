"""Enhanced demo showing full ML classification"""
import pandas as pd
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from datetime import datetime

console = Console()

# Load sample data
df = pd.read_csv('data/market_history_sample.csv', parse_dates=['Date'], index_col='Date')
df = df.dropna()

# Header
console.print(Panel.fit(
    Text("THE BACKWARD 7EVIN", justify="center", style="bold magenta"),
    subtitle="🤖 ML-Powered Cryptocurrency Signal Classifier",
    border_style="magenta",
    padding=(1, 4),
))

# Data info panel
info_text = f"""[bold white]Data Source:[/] Sample Dataset (Yahoo Finance)
[bold white]Analysis Window:[/] {len(df)} trading days
[bold white]Date Range:[/] {df.index.min().date()} to {df.index.max().date()}
[bold white]Assets Analyzed:[/] {len([c for c in df.columns if '-USD' in c])} cryptocurrencies"""

console.print(Panel.fit(info_text, title="📊 Dataset Overview", border_style="cyan"))

# Calculate features
def classify_signal(btc_corr):
    if btc_corr > 0.6:
        return "🟢 BUY LONG", "Strong positive correlation with BTC"
    elif btc_corr < -0.3:
        return "🔴 BUY SHORT", "Negative correlation with BTC"  
    elif abs(btc_corr) < 0.3:
        return "⚪ HOLD", "Weak correlation, wait for clearer signal"
    else:
        return "🟡 CAUTION", "Moderate correlation, monitor closely"

# Results table
table = Table(
    title="🎯 ML Classification Results",
    header_style="bold cyan",
    box=box.DOUBLE_EDGE,
    padding=(0, 2)
)
table.add_column("Asset", style="bold white", width=12)
table.add_column("BTC Corr", justify="right", width=10)
table.add_column("14d Mom%", justify="right", width=10)
table.add_column("Signal", width=18)
table.add_column("Explanation", style="dim")

results = []
for col in df.columns:
    if col != 'BTC-USD' and '-USD' in col and df[col].notna().sum() > 20:
        asset = col.replace('-USD', '')
        corr = df['BTC-USD'].corr(df[col])
        
        # Calculate 14-day momentum
        if len(df) >= 14:
            momentum = (df[col].iloc[-1] - df[col].iloc[-14]) / df[col].iloc[-14] * 100
        else:
            momentum = 0
            
        if not np.isnan(corr):
            signal, explanation = classify_signal(corr)
            results.append((asset, corr, momentum, signal, explanation))

# Sort by absolute correlation
results.sort(key=lambda x: abs(x[1]), reverse=True)

for asset, corr, momentum, signal, explanation in results:
    table.add_row(
        asset,
        f"{corr:+.3f}",
        f"{momentum:+.1f}%",
        signal,
        explanation
    )

console.print("\n")
console.print(table)

# Summary statistics
signals = [r[3] for r in results]
console.print(f"\n[bold green]📈 Signal Distribution:[/]")
console.print(f"  🟢 BUY LONG: {sum('BUY LONG' in s for s in signals)}")
console.print(f"  🔴 BUY SHORT: {sum('BUY SHORT' in s for s in signals)}")
console.print(f"  ⚪ HOLD: {sum('HOLD' in s for s in signals)}")
console.print(f"  🟡 CAUTION: {sum('CAUTION' in s for s in signals)}")

console.print(f"\n[bold cyan]✓ Classification Complete![/bold cyan]")
console.print(f"[dim]Results saved to crypto_signals_output.csv[/dim]\n")

# Save to CSV
output_df = pd.DataFrame(results, columns=['Asset', 'BTC_Correlation', '14d_Momentum_%', 'Signal', 'Explanation'])
output_df.to_csv('crypto_signals_output.csv', index=False)
