"""
The Backward 7evin - BEGINNER-FRIENDLY VERSION
Easy-to-read crypto buy/sell signals
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# SIMPLIFIED: Only analyze Bitcoin and Gold
ASSETS_TO_ANALYZE = ['BTC-USD', 'GC=F']
MARKET_CONTEXT = ['^GSPC', 'DX-Y.NYB']  # S&P 500 and USD Index for context

def fetch_market_data(symbols, days=90):
    """Fetch price data from Yahoo Finance"""
    end_date = datetime(2024, 10, 15)
    start_date = end_date - timedelta(days=days)
    data = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            if not df.empty:
                data[symbol] = df['Close']
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
    return pd.DataFrame(data)

def calculate_correlations(df, target_col):
    """Calculate how closely assets move together"""
    correlations = {}
    for col in df.columns:
        if col != target_col:
            corr = df[target_col].corr(df[col])
            correlations[col] = corr if not np.isnan(corr) else 0
    return correlations

def classify_signal(btc_corr, gold_corr, sp500_corr, usd_corr):
    """SIMPLE: If it moves with Bitcoin = BUY, opposite = SHORT, neither = HOLD"""
    if btc_corr > 0.2:  # Moves WITH Bitcoin
        return 'Buy Long'
    elif btc_corr < -0.15:  # Moves OPPOSITE Bitcoin
        return 'Buy Short'
    else:  # No clear trend
        return 'Hold'

def main():
    print("\n" + "="*60)
    print("  THE BACKWARD 7EVIN - SIMPLE VERSION")
    print("  Analyzing ONLY Bitcoin and Gold")
    print("="*60 + "\n")

    # Fetch data for ONLY Bitcoin and Gold
    print("📡 Fetching market data...")
    all_symbols = ASSETS_TO_ANALYZE + MARKET_CONTEXT
    full_df = fetch_market_data(all_symbols)
    full_df = full_df.dropna()
    print(f"✓ Loaded {len(full_df)} days of data")
    print(f"✓ Analyzing: Bitcoin and Gold ONLY\n")

    # Calculate signals for Bitcoin and Gold ONLY
    results = []

    # Analyze Bitcoin
    if 'BTC-USD' in full_df.columns:
        btc_df = full_df[['GC=F', '^GSPC', 'DX-Y.NYB', 'BTC-USD']]
        btc_correlations = calculate_correlations(btc_df, 'BTC-USD')
        btc_signal = classify_signal(
            1.0,  # Bitcoin correlates with itself
            btc_correlations.get('GC=F', 0),
            btc_correlations.get('^GSPC', 0),
            btc_correlations.get('DX-Y.NYB', 0))
        results.append({
            'Asset': 'Bitcoin',
            'BTC_Corr': 1.0,
            'Gold_Corr': btc_correlations.get('GC=F', 0),
            'Signal': btc_signal
        })

    # Analyze Gold
    if 'GC=F' in full_df.columns:
        gold_df = full_df[['BTC-USD', '^GSPC', 'DX-Y.NYB', 'GC=F']]
        gold_correlations = calculate_correlations(gold_df, 'GC=F')
        gold_signal = classify_signal(
            gold_correlations.get('BTC-USD', 0),
            1.0,  # Gold correlates with itself
            gold_correlations.get('^GSPC', 0),
            gold_correlations.get('DX-Y.NYB', 0))
        results.append({
            'Asset': 'Gold',
            'BTC_Corr': gold_correlations.get('BTC-USD', 0),
            'Gold_Corr': 1.0,
            'Signal': gold_signal
        })

    results_df = pd.DataFrame(results)

    # Display results
    print("="*70)
    print("ANALYSIS RESULTS - Bitcoin and Gold ONLY")
    print("="*70 + "\n")

    for _, row in results_df.iterrows():
        print(f"Asset: {row['Asset']}")
        print(f"  BTC Correlation: {row['BTC_Corr']:+.3f}")
        print(f"  Gold Correlation: {row['Gold_Corr']:+.3f}")
        print(f"  Signal: {row['Signal']}")
        print()

    print("="*70)
    print("📊 SUMMARY")
    print("="*70)
    for signal_type in ['Buy Long', 'Buy Short', 'Hold']:
        count = len(results_df[results_df['Signal'] == signal_type])
        if count > 0:
            print(f"  {signal_type}: {count}")
    print()
    print("📁 Results saved to: crypto_signals_output.csv\n")

    results_df.to_csv('crypto_signals_output.csv', index=False)

if __name__ == "__main__":
    main()
