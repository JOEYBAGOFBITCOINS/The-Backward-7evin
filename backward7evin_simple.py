"""
The Backward 7evin - BEGINNER-FRIENDLY VERSION
Easy-to-read crypto buy/sell signals
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Market data
MACRO_DRIVERS = {'BTC-USD': 'Bitcoin', 'GC=F': 'Gold', 'DX-Y.NYB': 'USD_Index', '^GSPC': 'SP500'}
CRYPTO_ASSETS = ['ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD', 'SOL-USD', 'DOGE-USD',
                 'MATIC-USD', 'DOT-USD', 'AVAX-USD', 'LINK-USD', 'UNI-USD', 'ATOM-USD']

def fetch_market_data(symbols, days=90):
    """Fetch price data from Yahoo Finance"""
    end_date = datetime.now()
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
    print("\n" + "🚀"*30)
    print("  THE BACKWARD 7EVIN - CRYPTO BUY/SELL SIGNALS")
    print("🚀"*30 + "\n")

    # Fetch data
    print("📡 Fetching market data...")
    all_symbols = list(MACRO_DRIVERS.keys()) + CRYPTO_ASSETS
    full_df = fetch_market_data(all_symbols)
    full_df = full_df.dropna()
    print(f"✓ Loaded {len(full_df)} days of data\n")

    # Calculate signals
    results = []
    for crypto in CRYPTO_ASSETS:
        if crypto in full_df.columns:
            crypto_df = full_df[['BTC-USD', 'GC=F', '^GSPC', 'DX-Y.NYB', crypto]]
            correlations = calculate_correlations(crypto_df, crypto)
            signal = classify_signal(
                correlations.get('BTC-USD', 0), correlations.get('GC=F', 0),
                correlations.get('^GSPC', 0), correlations.get('DX-Y.NYB', 0))
            results.append({
                'Asset': crypto.replace('-USD', ''),
                'BTC_Corr': correlations.get('BTC-USD', 0),
                'Signal': signal
            })

    results_df = pd.DataFrame(results)

    # Display in BEGINNER-FRIENDLY format
    buy_long = results_df[results_df['Signal'] == 'Buy Long']
    buy_short = results_df[results_df['Signal'] == 'Buy Short']
    hold = results_df[results_df['Signal'] == 'Hold']

    print("="*70)
    print("🟢 BUY LONG SIGNALS - These cryptos are BULLISH (moving up with Bitcoin)")
    print("="*70)
    if not buy_long.empty:
        for _, row in buy_long.iterrows():
            strength = "STRONG" if row['BTC_Corr'] > 0.6 else "MODERATE"
            print(f"  ✓ {row['Asset']:<10} {strength:<12} BTC Correlation: +{row['BTC_Corr']:.2f}")
            print(f"     → Action: Consider buying or holding long position")
            print()
    else:
        print("  (No bullish signals right now)\n")

    print("="*70)
    print("🔴 SHORT SIGNALS - These cryptos are BEARISH (moving opposite to Bitcoin)")
    print("="*70)
    if not buy_short.empty:
        for _, row in buy_short.iterrows():
            strength = "STRONG" if row['BTC_Corr'] < -0.4 else "MODERATE"
            print(f"  ✓ {row['Asset']:<10} {strength:<12} BTC Correlation: {row['BTC_Corr']:.2f}")
            print(f"     → Action: Consider shorting or avoiding")
            print()
    else:
        print("  (No bearish signals right now)\n")

    print("="*70)
    print("⚪ HOLD SIGNALS - These cryptos have NO CLEAR TREND (wait for signal)")
    print("="*70)
    if not hold.empty:
        for _, row in hold.iterrows():
            print(f"  ⏸ {row['Asset']:<10} NEUTRAL       BTC Correlation: {row['BTC_Corr']:+.2f}")
            print(f"     → Action: Wait - no clear signal yet")
            print()
    else:
        print("  (All cryptos have clear signals!)\n")

    print("="*70)
    print(f"📊 SUMMARY: {len(buy_long)} BUY | {len(buy_short)} SHORT | {len(hold)} HOLD")
    print("="*70)
    print("\n💡 TIP: Focus on STRONG signals for highest confidence trades")
    print("📁 Full data saved to: crypto_signals_output.csv\n")

    results_df.to_csv('crypto_signals_output.csv', index=False)

if __name__ == "__main__":
    main()
