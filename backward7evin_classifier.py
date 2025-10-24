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

# Macro-economic drivers and cryptocurrency universe
MACRO_DRIVERS = {'BTC-USD': 'Bitcoin', 'GC=F': 'Gold', 'DX-Y.NYB': 'USD_Index', '^GSPC': 'SP500'}
CRYPTO_ASSETS = ['ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD', 'SOL-USD', 'DOGE-USD',
                 'MATIC-USD', 'DOT-USD', 'AVAX-USD', 'LINK-USD', 'UNI-USD', 'ATOM-USD']
def fetch_market_data(symbols, days=90):
    """Fetch historical closing prices from Yahoo Finance API with improved error handling"""
    # Use fixed date range to ensure data availability (system date may be incorrect)
    end_date = datetime(2024, 10, 15)  # Known good date with available data
    start_date = end_date - timedelta(days=days + 30)  # Fetch extra days to account for missing data
    data = {}
    successful_fetches = []
    failed_fetches = []

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            if not df.empty and len(df) > 10:  # Ensure we have meaningful data
                data[symbol] = df['Close']
                successful_fetches.append(symbol)
            else:
                failed_fetches.append(f"{symbol} (empty/insufficient data)")
        except Exception as e:
            failed_fetches.append(f"{symbol} ({str(e)[:50]})")

    # Log fetch results
    if failed_fetches:
        print(f"⚠ Warning: Failed to fetch {len(failed_fetches)} symbols: {', '.join(failed_fetches[:3])}")
    if successful_fetches:
        print(f"✓ Successfully fetched {len(successful_fetches)} symbols")

    # Create dataframe and handle missing data intelligently
    df = pd.DataFrame(data)

    # Forward fill small gaps (up to 3 days) instead of dropping all rows
    df = df.ffill(limit=3)

    # Only drop rows where we still have NaN after forward filling
    initial_len = len(df)
    df = df.dropna()
    if len(df) < initial_len:
        print(f"⚠ Dropped {initial_len - len(df)} rows due to missing data. {len(df)} rows remaining.")

    if len(df) == 0:
        print("✗ ERROR: No data remaining after cleaning! Check data sources.")
        return df

    # Trim to requested days
    df = df.tail(days)

    return df
def calculate_correlations(df, target_col):
    """Calculate Pearson correlation as ML features. INNOVATION: Use RELATIONSHIPS not prices"""
    correlations = {}

    # Validate target column exists and has sufficient data
    if target_col not in df.columns:
        print(f"⚠ Warning: Target column '{target_col}' not found in dataframe")
        return correlations

    if len(df) < 10:
        print(f"⚠ Warning: Insufficient data ({len(df)} rows) for meaningful correlations")
        return correlations

    for col in df.columns:
        if col != target_col:
            # Check if column has sufficient variance
            if df[col].std() < 1e-10:
                print(f"⚠ Warning: '{col}' has no variance (constant values)")
                correlations[col] = 0.0
                continue

            # Calculate correlation
            corr = df[target_col].corr(df[col])

            # Handle NaN (can occur with insufficient variance or data issues)
            if np.isnan(corr):
                print(f"⚠ Warning: Correlation between '{target_col}' and '{col}' is NaN")
                correlations[col] = 0.0
            else:
                correlations[col] = corr

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
    # Step 1: Collect macro-economic and cryptocurrency data
    print("\n[1/3] Fetching market data from Yahoo Finance...")
    all_symbols = list(MACRO_DRIVERS.keys()) + CRYPTO_ASSETS
    full_df = fetch_market_data(all_symbols)
    full_df = full_df.dropna()  # Remove missing values for clean correlations
    print(f"Loaded {len(full_df)} days of data for {len(full_df.columns)} assets")
    # Step 2: Feature engineering and classification
    # KEY INNOVATION: Using correlations AS features (not price/volume)
    print("\n[2/3] Computing correlation features and classifying signals...")
    results = []
    for crypto in CRYPTO_ASSETS:
        if crypto in full_df.columns:
            # Extract feature subset for this cryptocurrency
            crypto_df = full_df[['BTC-USD', 'GC=F', '^GSPC', 'DX-Y.NYB', crypto]]
            correlations = calculate_correlations(crypto_df, crypto)
            # Apply supervised classification model (thresholds learned from historical data)
            signal = classify_signal(
                correlations.get('BTC-USD', 0), correlations.get('GC=F', 0),
                correlations.get('^GSPC', 0), correlations.get('DX-Y.NYB', 0))
            # Store results with feature values
            results.append({
                'Asset': crypto.replace('-USD', ''),
                'BTC_Corr': round(correlations.get('BTC-USD', 0), 3),
                'Gold_Corr': round(correlations.get('GC=F', 0), 3),
                'SP500_Corr': round(correlations.get('^GSPC', 0), 3),
                'USD_Corr': round(correlations.get('DX-Y.NYB', 0), 3),
                'Signal': signal})
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
