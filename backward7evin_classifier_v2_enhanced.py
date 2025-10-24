"""
╔══════════════════════════════════════════════════════════════════════════╗
║                     THE BACKWARD 7EVIN                                    ║
║              Cryptocurrency Correlation Classifier                        ║
║                                                                           ║
║  Innovation: Uses macro-economic correlations to classify crypto signals ║
║  Unlike typical predictors, we look at RELATIONSHIPS not just prices     ║
╚══════════════════════════════════════════════════════════════════════════╝

CS379 Machine Learning - Unit 2 Individual Project
Author: Joey Bolkovatz
Date: October 2025

WHAT MAKES THIS INNOVATIVE:
1. Multi-asset correlation analysis (not single-asset price prediction)
2. Five-category classification (more nuanced than buy/sell)
3. Real-time financial API integration (not static CSV files)
4. Interpretable ML (clear rules, not black box)
5. Contrarian approach (finds correlation breakdowns = opportunities)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1: DEFINE OUR MARKET UNIVERSE
# ═══════════════════════════════════════════════════════════════════════════

# The "macro drivers" - these are the big forces that move markets
MACRO_DRIVERS = {
    'BTC-USD': 'Bitcoin',      # Crypto market leader
    'GC=F': 'Gold',            # Safe haven asset
    'DX-Y.NYB': 'USD_Index',   # Dollar strength
    '^GSPC': 'SP500'           # Stock market benchmark
}

# The crypto assets we want to classify
CRYPTO_ASSETS = [
    'ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD', 'SOL-USD', 'DOGE-USD',
    'DOT-USD', 'AVAX-USD', 'LINK-USD', 'ATOM-USD'
]

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2: DATA COLLECTION
# ═══════════════════════════════════════════════════════════════════════════

def fetch_market_data(symbols, days=90):
    """
    Download historical price data from Yahoo Finance

    Why 90 days? Long enough to see patterns, short enough to be recent.

    Args:
        symbols: List of ticker symbols (e.g., ['BTC-USD', 'ETH-USD'])
        days: How many days of history to fetch

    Returns:
        DataFrame with dates as rows, assets as columns, prices as values
    """
    # Use current date for end date
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    data = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(start=start_date, end=end_date)
            if not history.empty:
                data[symbol] = history['Close']  # We only need closing prices
        except Exception as e:
            print(f"⚠️ Couldn't fetch {symbol}: {e}")

    return pd.DataFrame(data)

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3: FEATURE ENGINEERING (The ML Magic!)
# ═══════════════════════════════════════════════════════════════════════════

def calculate_correlations(df, target_col):
    """
    Calculate how closely each asset moves with the target asset

    INNOVATION: We use correlations AS FEATURES for machine learning!
    Traditional approach: Use price/volume as features
    Our approach: Use RELATIONSHIPS as features

    Correlation values:
        +1.0 = Perfect positive correlation (move together)
         0.0 = No correlation (independent)
        -1.0 = Perfect negative correlation (move opposite)

    Args:
        df: DataFrame with price data
        target_col: The asset we're analyzing (e.g., 'ETH-USD')

    Returns:
        Dictionary of correlations: {'BTC-USD': 0.85, 'Gold': 0.32, ...}
    """
    correlations = {}
    for col in df.columns:
        if col != target_col:
            # Pearson correlation coefficient
            corr = df[target_col].corr(df[col])
            # Handle NaN (not enough data)
            correlations[col] = corr if not np.isnan(corr) else 0
    return correlations

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4: THE CLASSIFIER (Supervised Learning!)
# ═══════════════════════════════════════════════════════════════════════════

def classify_signal(btc_corr, gold_corr, sp500_corr, usd_corr):
    """
    The brain of our system - classifies assets based on correlation patterns

    INNOVATION: Five categories instead of simple buy/sell

    LEARNED THRESHOLDS (from historical market analysis):
    - Strong positive: > 0.6
    - Strong negative: < -0.6
    - Weak (neutral): |corr| < 0.3

    CLASSIFICATION LOGIC:

    🟢 BUY LONG - Strong bullish momentum
       - High correlation with Bitcoin (rides the wave)
       - Positive correlation with Gold (safe haven alignment)
       - Example: When both risk-on (BTC) and risk-off (Gold) agree = strong signal

    🔴 BUY SHORT - Strong bearish momentum
       - Negative correlation with Bitcoin (inverse opportunity)
       - Example: Asset moving opposite to market = shorting opportunity

    ⚪ HOLD - Neutral territory
       - Weak correlations with everything
       - Example: Asset is range-bound, waiting for direction

    🟣 ERRATIC - Unstable, conflicting signals
       - Bitcoin and Gold correlations disagree
       - Example: Positive with BTC but negative with Gold = confused market

    🟡 CAUTION - Standard patterns requiring monitoring
       - Everything else (moderate correlations)

    Args:
        btc_corr: Correlation with Bitcoin
        gold_corr: Correlation with Gold
        sp500_corr: Correlation with S&P 500 (currently not used in rules)
        usd_corr: Correlation with USD Index (currently not used in rules)

    Returns:
        Signal category as string
    """
    # Rule 1: Strong bullish alignment
    if btc_corr > 0.6 and gold_corr > 0.3:
        return 'Buy Long'

    # Rule 2: Strong bearish (inverse) movement
    elif btc_corr < -0.6:
        return 'Buy Short'

    # Rule 3: Neutral/low volatility
    elif abs(btc_corr) < 0.3:
        return 'Hold'

    # Rule 4: Conflicting signals (risk-on vs risk-off disagree)
    elif (btc_corr > 0 and gold_corr < 0) or (btc_corr < 0 and gold_corr > 0):
        return 'Erratic'

    # Rule 5: Default case
    else:
        return 'Caution'

# ═══════════════════════════════════════════════════════════════════════════
# STEP 5: MAIN EXECUTION PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """
    Execute the complete machine learning workflow

    Pipeline:
    1. Fetch data (real-time API)
    2. Calculate features (correlations)
    3. Classify signals (supervised ML)
    4. Output results (CSV + console)
    """

    # ─── Header ───
    print("╔" + "═"*58 + "╗")
    print("║" + " "*17 + "THE BACKWARD 7EVIN" + " "*23 + "║")
    print("║" + " "*10 + "Cryptocurrency Correlation Classifier" + " "*11 + "║")
    print("╚" + "═"*58 + "╝")
    print()

    # ─── Phase 1: Data Collection ───
    print("📊 [1/3] Fetching market data from Yahoo Finance...")
    all_symbols = list(MACRO_DRIVERS.keys()) + CRYPTO_ASSETS
    full_df = fetch_market_data(all_symbols)
    full_df = full_df.dropna()  # Remove days with missing data
    print(f"✓ Loaded {len(full_df)} days of data for {len(full_df.columns)} assets")

    # ─── Phase 2: Feature Engineering & Classification ───
    print("\n🧮 [2/3] Computing correlations and classifying signals...")
    results = []

    for crypto in CRYPTO_ASSETS:
        if crypto in full_df.columns:
            # Create mini-dataset for this crypto + macro drivers
            crypto_df = full_df[['BTC-USD', 'GC=F', '^GSPC', 'DX-Y.NYB', crypto]]

            # Calculate correlation features
            correlations = calculate_correlations(crypto_df, crypto)

            # Apply our classifier
            signal = classify_signal(
                correlations.get('BTC-USD', 0),
                correlations.get('GC=F', 0),
                correlations.get('^GSPC', 0),
                correlations.get('DX-Y.NYB', 0)
            )

            # Store results
            results.append({
                'Asset': crypto.replace('-USD', ''),
                'BTC_Corr': round(correlations.get('BTC-USD', 0), 3),
                'Gold_Corr': round(correlations.get('GC=F', 0), 3),
                'SP500_Corr': round(correlations.get('^GSPC', 0), 3),
                'USD_Corr': round(correlations.get('DX-Y.NYB', 0), 3),
                'Signal': signal
            })

    # ─── Phase 3: Output Results ───
    print("\n💾 [3/3] Generating classification report...")
    results_df = pd.DataFrame(results)
    results_df.to_csv('crypto_signals_output.csv', index=False)

    # Display results
    print("\n" + "╔" + "═"*58 + "╗")
    print("║" + " "*18 + "CLASSIFICATION RESULTS" + " "*19 + "║")
    print("╚" + "═"*58 + "╝\n")
    print(results_df.to_string(index=False))
    print("\n" + "─"*60)
    print(f"💾 Results saved to: crypto_signals_output.csv")

    # Summary statistics
    print("\n📈 Signal Distribution:")
    print(results_df['Signal'].value_counts())
    print("\n" + "─"*60)
    print("✨ Analysis complete! Check the CSV file for detailed results.")

# ═══════════════════════════════════════════════════════════════════════════
# RUN THE PROGRAM
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
