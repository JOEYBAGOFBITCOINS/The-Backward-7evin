"""
Diagnostic script to identify correlation calculation issues
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Test data fetching
print("="*60)
print("DIAGNOSTIC: Testing Data Fetching and Correlations")
print("="*60)

end_date = datetime(2024, 10, 15)
start_date = end_date - timedelta(days=90)

symbols = ['BTC-USD', 'ETH-USD', 'GC=F', '^GSPC', 'DX-Y.NYB']

print(f"\nFetching data from {start_date.date()} to {end_date.date()}...")
data = {}
for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        if not df.empty:
            data[symbol] = df['Close']
            print(f"✓ {symbol}: {len(df)} data points")
        else:
            print(f"✗ {symbol}: NO DATA RECEIVED")
    except Exception as e:
        print(f"✗ {symbol}: ERROR - {e}")

# Create dataframe
df = pd.DataFrame(data)
print(f"\n{'='*60}")
print(f"Combined DataFrame Shape: {df.shape}")
print(f"{'='*60}")
print("\nFirst 5 rows:")
print(df.head())
print("\nLast 5 rows:")
print(df.tail())
print(f"\n{'='*60}")
print("Missing Values:")
print(df.isnull().sum())
print(f"\n{'='*60}")

# Drop NaN and recheck
df_clean = df.dropna()
print(f"After dropna: {df_clean.shape}")
print("\nFirst 5 rows after cleaning:")
print(df_clean.head())

# Calculate correlations with ETH
if 'ETH-USD' in df_clean.columns and len(df_clean) > 1:
    print(f"\n{'='*60}")
    print("CORRELATION ANALYSIS: ETH-USD")
    print(f"{'='*60}")

    for col in df_clean.columns:
        if col != 'ETH-USD':
            corr = df_clean['ETH-USD'].corr(df_clean[col])
            print(f"{col:20} -> ETH-USD: {corr:.6f}")
else:
    print("\n✗ ERROR: Cannot calculate correlations - insufficient data")

print(f"\n{'='*60}")
print("DIAGNOSIS COMPLETE")
print(f"{'='*60}")
