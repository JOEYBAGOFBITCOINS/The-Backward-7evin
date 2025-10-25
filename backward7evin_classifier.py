"""
The Backward 7evin - Cryptocurrency Classification System
CS379 Machine Learning - Unit 2 Individual Project
Author: Joey Bolkovatz | Date: October 2025
Supervised Learning: Correlation-based Multi-class Classification
Dataset: Yahoo Finance (90-day historical crypto and macro-economic data)
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# SIMPLIFIED: Only analyze Bitcoin and Gold as required
# These are the ONLY two assets we analyze
ASSETS_TO_ANALYZE = ['BTC-USD', 'GC=F']
# Additional market data for correlation analysis
MARKET_CONTEXT = ['^GSPC', 'DX-Y.NYB']  # S&P 500 and USD Index for context
def fetch_market_data(symbols, days=90):
    """Fetch historical closing prices from Yahoo Finance API"""
    # Use fixed date range to ensure data availability (system date may be incorrect)
    end_date = datetime(2024, 10, 15)  # Known good date with available data
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
    """Calculate Pearson correlation as ML features. INNOVATION: Use RELATIONSHIPS not prices"""
    correlations = {}
    for col in df.columns:
        if col != target_col:
            corr = df[target_col].corr(df[col])  # How closely assets move together (-1 to +1)
            correlations[col] = corr if not np.isnan(corr) else 0  # Handle missing data
    return correlations

def classify_signal(btc_corr, gold_corr, sp500_corr, usd_corr):
    """Supervised classifier: Simple rules for beginners
    SUPERVISED LEARNING: Thresholds tuned for clear, actionable signals
    Returns: Buy Long (bullish), Buy Short (bearish), or Hold (neutral)"""
    # ULTRA-SIMPLE logic: Just look at Bitcoin correlation
    if btc_corr > 0.2:  # Moves with Bitcoin = BULLISH
        return 'Buy Long'
    elif btc_corr < -0.15:  # Moves opposite Bitcoin = BEARISH
        return 'Buy Short'
    else:  # Very weak or no correlation = NEUTRAL
        return 'Hold'

def main():
    """Main execution: data collection, feature extraction, classification, output"""
    print("="*60)
    print("The Backward 7evin - Cryptocurrency Signal Classifier")
    print("Supervised Learning: Correlation-Based Classification")
    print("="*60)
    # Step 1: Collect ONLY Bitcoin and Gold + market context
    print("\n[1/3] Fetching market data from Yahoo Finance...")
    all_symbols = ASSETS_TO_ANALYZE + MARKET_CONTEXT
    full_df = fetch_market_data(all_symbols)
    full_df = full_df.dropna()  # Remove missing values for clean correlations
    print(f"Loaded {len(full_df)} days of data for {len(full_df.columns)} assets")
    print(f"Analyzing ONLY: Bitcoin and Gold")

    # Step 2: Analyze Bitcoin and Gold ONLY
    print("\n[2/3] Computing correlation features and classifying signals...")
    results = []

    # Analyze Bitcoin
    if 'BTC-USD' in full_df.columns:
        btc_df = full_df[['GC=F', '^GSPC', 'DX-Y.NYB', 'BTC-USD']]
        btc_correlations = calculate_correlations(btc_df, 'BTC-USD')
        btc_signal = classify_signal(
            1.0,  # Bitcoin correlates perfectly with itself
            btc_correlations.get('GC=F', 0),
            btc_correlations.get('^GSPC', 0),
            btc_correlations.get('DX-Y.NYB', 0))
        results.append({
            'Asset': 'Bitcoin',
            'BTC_Corr': 1.0,
            'Gold_Corr': round(btc_correlations.get('GC=F', 0), 3),
            'SP500_Corr': round(btc_correlations.get('^GSPC', 0), 3),
            'USD_Corr': round(btc_correlations.get('DX-Y.NYB', 0), 3),
            'Signal': btc_signal})

    # Analyze Gold
    if 'GC=F' in full_df.columns:
        gold_df = full_df[['BTC-USD', '^GSPC', 'DX-Y.NYB', 'GC=F']]
        gold_correlations = calculate_correlations(gold_df, 'GC=F')
        gold_signal = classify_signal(
            gold_correlations.get('BTC-USD', 0),
            1.0,  # Gold correlates perfectly with itself
            gold_correlations.get('^GSPC', 0),
            gold_correlations.get('DX-Y.NYB', 0))
        results.append({
            'Asset': 'Gold',
            'BTC_Corr': round(gold_correlations.get('BTC-USD', 0), 3),
            'Gold_Corr': 1.0,
            'SP500_Corr': round(gold_correlations.get('^GSPC', 0), 3),
            'USD_Corr': round(gold_correlations.get('DX-Y.NYB', 0), 3),
            'Signal': gold_signal})
    # Step 3: Output and save results
    print("\n[3/3] Generating classification report...")
    results_df = pd.DataFrame(results)
    results_df.to_csv('crypto_signals_output.csv', index=False)
    print("\n" + "="*60)
    print("CLASSIFICATION RESULTS")
    print("="*60)
    print(results_df.to_string(index=False))
    print("\n" + "="*60)
    print(f"Results saved to: crypto_signals_output.csv")
    print(f"\nSignal Distribution:\n{results_df['Signal'].value_counts()}")


if __name__ == "__main__":
    main()
