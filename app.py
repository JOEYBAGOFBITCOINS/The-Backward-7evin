import warnings
warnings.filterwarnings("ignore")

# ===== Core imports =====
import time
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# Forecasting
try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from statsmodels.tsa.arima.model import ARIMA
    STATS_OK = True
except Exception:
    STATS_OK = False

# ML
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix

# Viz
import plotly.graph_objects as go

# ===== App constants =====
APP_TITLE = "Backward 7evin"
ASSETS = {
    "BTC-USD": "Bitcoin",
    "GC=F": "Gold",
    "DX-Y.NYB": "USD"
}

# ===== Page and theme =====
st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")
st.markdown(
    """
    <style>
    .stApp{
      background: radial-gradient(circle at 10% 20%, #0f0f14 0%, #0a0a0e 100%);
      color:#e6e6e6;
    }
    .glass{
      background: rgba(255,255,255,0.03);
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 16px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.45);
      backdrop-filter: blur(10px);
      padding: 18px 20px;
    }
    .signal{
      font-weight: 700; font-size: 22px; letter-spacing:.3px;
      padding: 8px 14px; border-radius: 12px; display:inline-block;
    }
    .long  { background: rgba(22,163,74,0.2);  border: 1px solid rgba(22,163,74,0.5); }
    .short { background: rgba(220,38,38,0.2);  border: 1px solid rgba(220,38,38,0.5); }
    .hold  { background: rgba(148,163,184,0.2); border: 1px solid rgba(148,163,184,0.5); }
    .metric { font-size: 14px; color: #b3b3b3; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title(APP_TITLE)

# ===== 1-minute auto refresh =====
# Try native component if available, else fallback to simple timer rerun
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=60_000, key="live_refresh")
except Exception:
    now = time.time()
    if "last_refresh_ts" not in st.session_state:
        st.session_state["last_refresh_ts"] = now
    elif now - st.session_state["last_refresh_ts"] > 60:
        st.session_state["last_refresh_ts"] = now
        st.experimental_rerun()

# ===== Helpers =====
@st.cache_data(ttl=900)
def fetch_prices(period="180d", interval="1d") -> pd.DataFrame:
    """
    Pulls OHLC close prices for BTC, Gold, and USD index via yfinance.
    Returns a DataFrame with renamed columns for readability.
    """
    df = yf.download(list(ASSETS.keys()), period=period, interval=interval, progress=False)["Close"]
    if isinstance(df, pd.Series):
        df = df.to_frame()
    df = df.dropna()
    df.columns = [ASSETS.get(c, c) for c in df.columns]
    return df

def compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def fib_levels(series: pd.Series) -> dict:
    hi, lo = series.max(), series.min()
    d = hi - lo
    return {
        "Fib 23.6%": hi - d * 0.236,
        "Fib 38.2%": hi - d * 0.382,
        "Fib 50.0%": hi - d * 0.5,
        "Fib 61.8%": hi - d * 0.618
    }

def try_arima(series: pd.Series) -> pd.Series:
    if not STATS_OK:
        return pd.Series(dtype=float)
    try:
        res = ARIMA(series.dropna(), order=(1, 1, 1)).fit()
        return res.forecast(5)
    except Exception:
        return pd.Series(dtype=float)

def try_hw(series: pd.Series) -> pd.Series:
    if not STATS_OK:
        return pd.Series(dtype=float)
    try:
        res = ExponentialSmoothing(series.dropna(), trend="add").fit()
        return res.forecast(5)
    except Exception:
        return pd.Series(dtype=float)

# ===== Feature engineering for ML (supervised) =====
def build_features(df: pd.DataFrame) -> pd.DataFrame:
    feats = pd.DataFrame(index=df.index)
    for col in df.columns:
        feats[f"{col}_ret1"] = df[col].pct_change()
        feats[f"{col}_ret5"] = df[col].pct_change(5)
        feats[f"{col}_vol10"] = df[col].pct_change().rolling(10).std()
    if "Bitcoin" in df:
        feats["BTC_RSI"] = compute_rsi(df["Bitcoin"])
        feats["BTC_MA7"] = df["Bitcoin"].rolling(7).mean()
        feats["BTC_MA21"] = df["Bitcoin"].rolling(21).mean()
        feats["BTC_MA_diff"] = feats["BTC_MA7"] - feats["BTC_MA21"]
    if set(["Bitcoin", "Gold"]).issubset(df.columns):
        feats["corr_BTC_Gold"] = df["Bitcoin"].rolling(20).corr(df["Gold"])
    if set(["Bitcoin", "USD"]).issubset(df.columns):
        feats["corr_BTC_USD"] = df["Bitcoin"].rolling(20).corr(df["USD"])
    return feats.dropna()

def label_target(df: pd.DataFrame) -> pd.Series:
    # Predict next day BTC up (1) or down (0)
    return (df["Bitcoin"].shift(-1) > df["Bitcoin"]).astype(int)

# ===== Models =====
def train_rf(df: pd.DataFrame):
    X = build_features(df)
    y = label_target(df).reindex(X.index)
    data = pd.concat([X, y.rename("target")], axis=1).dropna()
    if len(data) < 120:
        return None
    X_train, X_test, y_train, y_test = train_test_split(
        data.drop(columns=["target"]), data["target"], test_size=0.2, shuffle=False
    )
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    rf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    rf.fit(X_train_s, y_train)
    preds = rf.predict(X_test_s)
    acc = accuracy_score(y_test, preds)
    latest = scaler.transform(X.tail(1))
    proba = rf.predict_proba(latest)[0]
    pred = rf.predict(latest)[0]
    signal = "LONG" if pred == 1 else "SHORT"
    conf = float(max(proba)) * 100.0
    return {"model": rf, "scaler": scaler, "accuracy": acc, "signal": signal, "confidence": conf}

def train_ensemble(df: pd.DataFrame):
    X = build_features(df)
    y = label_target(df).reindex(X.index)
    data = pd.concat([X, y.rename("target")], axis=1).dropna()
    if len(data) < 120:
        return None
    X_train, X_test, y_train, y_test = train_test_split(
        data.drop(columns=["target"]), data["target"], test_size=0.2, shuffle=False
    )
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    rf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    gb = GradientBoostingClassifier(random_state=42)
    lr = LogisticRegression(max_iter=1000)

    ens = VotingClassifier(
        estimators=[("rf", rf), ("gb", gb), ("lr", lr)],
        voting="soft"
    )
    ens.fit(X_train_s, y_train)
    acc = ens.score(X_test_s, y_test)

    latest = scaler.transform(X.tail(1))
    proba = ens.predict_proba(latest)[0]
    pred = ens.predict(latest)[0]
    signal = "LONG" if pred == 1 else "SHORT"
    conf = float(max(proba)) * 100.0

    # Individual votes for transparency
    votes = {
        "Random Forest": "LONG" if rf.fit(X_train_s, y_train).predict(latest)[0] == 1 else "SHORT",
        "Gradient Boost": "LONG" if gb.fit(X_train_s, y_train).predict(latest)[0] == 1 else "SHORT",
        "Logistic Reg": "LONG" if lr.fit(X_train_s, y_train).predict(latest)[0] == 1 else "SHORT",
    }
    return {"model": ens, "scaler": scaler, "accuracy": acc,
            "signal": signal, "confidence": conf, "votes": votes}

# ===== Sidebar =====
    st.subheader("Models")
    use_arima = st.checkbox("ARIMA Forecast", value=True, key="arima_checkbox")
    use_hw = st.checkbox("Holt–Winters Forecast", value=True, key="holtwinters_checkbox")
    use_rf = st.checkbox("Random Forest Signal", value=True, key="rf_checkbox")
    use_ens = st.checkbox("Use Ensemble Model", value=True, key="ensemble_checkbox")
    st.divider()
    st.caption("Live data refresh is set to 1 minute.")


if "last_model_state" not in st.session_state or st.session_state["last_model_state"] != use_ens:
    st.session_state["last_model_state"] = use_ens
    st.rerun()

# ===== Load data =====
raw = fetch_prices(period=period, interval=interval)
if raw.empty:
    st.error("No data available. Try another window or interval.")
    st.stop()

# ===== Top glass panel =====
st.markdown("<div class='glass'>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns([2, 2, 2, 3])
latest = raw.iloc[-1]
c1.metric("Bitcoin", f"${latest['Bitcoin']:.2f}")
# ===== Sidebar =====
# ===== Sidebar =====
    st.subheader("Models")
    use_arima = st.checkbox("ARIMA Forecast", value=True)
    use_hw = st.checkbox("Holt–Winters Forecast", value=True)
    use_rf = st.checkbox("Random Forest Signal", value=True)
    use_ens = st.checkbox("Use Ensemble Model", value=True)
    st.divider()
    st.caption("Live data refresh is set to 1 minute.")

# ===== Refresh when ensemble toggle changes =====
if "last_model_state" not in st.session_state or st.session_state["last_model_state"] != use_ens:
    st.session_state["last_model_state"] = use_ens
    st.rerun()

# ===== Load data =====
try:
    with st.spinner("Fetching live market data..."):
        raw = fetch_prices(period=period, interval=interval)
except Exception as e:
    st.error(f"Data temporarily unavailable. Please try again shortly.\nDetails: {e}")
    st.stop()

if raw.empty:
    st.error("No data available. Try another window or interval.")
    st.stop()

# ===== Top glass panel =====
st.markdown("<div class='glass'>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns([2, 2, 2, 3])
latest = raw.iloc[-1]
c1.metric("Bitcoin", f"${latest['Bitcoin']:.2f}")
c2.metric("Gold", f"${latest['Gold']:.2f}")
c3.metric("USD Index", f"{latest['USD']:.2f}")

# ===== Train models =====
with st.spinner("Training models..."):
    rf_res = train_rf(raw) if use_rf else None
    ens_res = train_ensemble(raw) if use_ens else None

def action_from_signal(sig, conf):
    if sig == "LONG":
        return "🟢 Full Green Light — Go LONG" if conf >= 80 else "🟡 Caution — Prefer LONG, size conservatively"
    else:
        return "🔴 Red Light — Go SHORT" if conf >= 80 else "🟡 Caution — Prefer SHORT, size conservatively"

action_text = "HOLD — Mixed conditions"
if ens_res:
    action_text = action_from_signal(ens_res["signal"], ens_res["confidence"])
elif rf_res:
    action_text = action_from_signal(rf_res["signal"], rf_res["confidence"])

c4.markdown(f"**AI Direction**<br>{action_text}", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.divider()

# ===== Tabs =====
t1, t2, t3, t4 = st.tabs(["Charts", "Forecasts", "Fibonacci", "Ensemble"])

# Charts
with t1:
    st.subheader("Price Charts")
    for key, name in ASSETS.items():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=raw.index, y=raw[name], mode="lines", name=name))
        fig.update_layout(template="plotly_dark", height=380, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

# Forecasts
with t2:
    st.subheader("Forecasts — next 5 steps")
    summary = []

    def summarize(series: pd.Series):
        if series is None or series.empty:
            return "Flat", 0.0
        start, end = float(series.iloc[0]), float(series.iloc[-1])
        pct = (end - start) / max(1e-9, abs(start)) * 100.0
        if pct > 0.1:
            return "Bullish", pct
        if pct < -0.1:
            return "Bearish", pct
        return "Flat", pct

    cols = st.columns(3)
    for i, (key, name) in enumerate(ASSETS.items()):
        series = raw[name]
        a = try_arima(series) if use_arima else pd.Series(dtype=float)
        h = try_hw(series) if use_hw else pd.Series(dtype=float)
        a_dir, a_pct = summarize(a)
        h_dir, h_pct = summarize(h)
        icon = {"Bullish": "🟢", "Bearish": "🔴", "Flat": "⚪"}

        with cols[i % 3]:
            st.markdown(f"### {name}")
            st.write(f"ARIMA: {icon[a_dir]} {a_dir} ({a_pct:+.2f}%)")
            st.write(f"Holt–Winters: {icon[h_dir]} {h_dir} ({h_pct:+.2f}%)")

        summary.append((name, a_dir, a_pct, h_dir, h_pct))

    st.markdown("---")
    st.markdown("**Summary**")
    for name, a_dir, a_pct, h_dir, h_pct in summary:
        icon = {"Bullish": "🟢", "Bearish": "🔴", "Flat": "⚪"}
        st.write(
            f"{name}: ARIMA {icon[a_dir]} {a_dir} ({a_pct:+.2f}%), "
            f"Holt–Winters {icon[h_dir]} {h_dir} ({h_pct:+.2f}%)"
        )

# Fibonacci
with t3:
    st.subheader("Fibonacci Levels")
    for k, name in ASSETS.items():
        st.markdown(f"### {name}")
        st.markdown("**Fibonacci Retracement Levels:**")
        for nm, val in fib_levels(raw[name]).items():
            st.write(f"• **{nm}** → ${val:,.2f}")
        st.divider()

# Ensemble tab
with t4:
    st.subheader("Ensemble Signals")
    if ens_res:
        sig, conf = ens_res["signal"], ens_res["confidence"]
        css = "long" if sig == "LONG" else "short"
        st.markdown(f"<div class='signal {css}'>Overall: {sig} {conf:.1f}%</div>", unsafe_allow_html=True)
        st.markdown("**Model Votes**")
        st.write({
            "Random Forest": ens_res["votes"]["Random Forest"],
            "Gradient Boost": ens_res["votes"]["Gradient Boost"],
            "Logistic Reg": ens_res["votes"]["Logistic Reg"],
        })
        st.caption("Guidance: ≥ 80% confidence → Full Green or Red. Mixed → Caution or Hold.")
    else:
        st.info("Enable Use Ensemble Model in the sidebar to view combined signals.")

