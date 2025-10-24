"""
Diagnostic script to test Yahoo Finance data fetching
"""
import yfinance as yf
from datetime import datetime, timedelta

print("Testing Yahoo Finance data fetching...")
print(f"Current time: {datetime.now()}")
print()

# Test with current date
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

print(f"Date range: {start_date.date()} to {end_date.date()}")
print()

# Test BTC-USD
print("Fetching BTC-USD...")
try:
    ticker = yf.Ticker('BTC-USD')
    history = ticker.history(start=start_date, end=end_date)
    print(f"✓ Rows returned: {len(history)}")
    if not history.empty:
        print(f"  First date: {history.index[0]}")
        print(f"  Last date: {history.index[-1]}")
        print(f"  First close price: ${history['Close'].iloc[0]:.2f}")
        print(f"  Last close price: ${history['Close'].iloc[-1]:.2f}")
    else:
        print("  WARNING: Empty DataFrame returned!")
except Exception as e:
    print(f"✗ Error: {e}")

print()

# Test ETH-USD
print("Fetching ETH-USD...")
try:
    ticker = yf.Ticker('ETH-USD')
    history = ticker.history(start=start_date, end=end_date)
    print(f"✓ Rows returned: {len(history)}")
    if not history.empty:
        print(f"  First date: {history.index[0]}")
        print(f"  Last date: {history.index[-1]}")
    else:
        print("  WARNING: Empty DataFrame returned!")
except Exception as e:
    print(f"✗ Error: {e}")

print()

# Test with period instead of dates
print("Testing with period='3mo' instead of date range...")
try:
    ticker = yf.Ticker('BTC-USD')
    history = ticker.history(period='3mo')
    print(f"✓ Rows returned: {len(history)}")
    if not history.empty:
        print(f"  First date: {history.index[0]}")
        print(f"  Last date: {history.index[-1]}")
    else:
        print("  WARNING: Empty DataFrame returned!")
except Exception as e:
    print(f"✗ Error: {e}")
