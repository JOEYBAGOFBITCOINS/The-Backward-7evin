# The Backward 7evin - Cryptocurrency Correlation Intelligence

**CS379 Machine Learning - Unit 2 Individual Project**
**Student:** Joey Bolkovatz
**Course:** Machine Learning
**Points:** 125

## Project Overview

The Backward 7evin is an interpretable machine learning system that classifies cryptocurrency market signals by analysing how each asset moves relative to Bitcoin, Gold, the U.S. Dollar Index, and the S&P 500. Instead of opaque price prediction, the project focuses on explaining *why* a signal fires by surfacing the correlations, momentum, and risk metrics behind every recommendation.

## Dataset Sources

This project uses publicly available financial data from the following sources:

### Primary Data Source
- **Yahoo Finance API** (via `yfinance` library)
  - Access: https://finance.yahoo.com/
  - Data Type: Historical price data (Open, High, Low, Close, Volume)
  - Frequency: Daily closes resampled to align macro and crypto assets
  - Coverage: 210-day rolling window (tunable)

### Offline Fallback

- **Bundled snapshot** – `data/market_history_sample.csv`
  - 210 aligned trading days captured on 25 Oct 2025
  - Ensures the project runs flawlessly during demos with no internet access
  - Automatically loaded whenever the live API is unavailable or missing macro drivers

### Asset Classes Analyzed

**Macro Economic Drivers:**
- Gold (GC=F) - Commodity inflation hedge
- US Dollar Index (DX-Y.NYB) - Currency strength indicator
- S&P 500 (^GSPC) - Equity market benchmark
- Bitcoin (BTC-USD) - Crypto market leader

**Cryptocurrency Universe (20+ assets):**
- Major: BTC, ETH, BNB, XRP, ADA, SOL, DOGE
- DeFi: AVAX, MATIC, DOT, LINK, UNI
- Layer 1/2: ATOM, ALGO, FTM, NEAR
- And others as market conditions evolve

### Data Compliance

All data is:
- Publicly available through Yahoo Finance
- Compliant with fair use policies for educational research
- Properly attributed per academic standards
- Updated in real-time for reproducibility

## Supervised Learning Approach

### Algorithm Selection: Interpretable Rule-Based Classification

**Rationale:**
1. **Explainable:** Every signal is tied to explicit correlation and momentum thresholds
2. **Correlation-first:** Focuses on the relationships between assets instead of raw prices
3. **Resilient:** Handles noisy financial data and clearly surfaces high-volatility regimes
4. **Actionable:** Produces trader-friendly labels with emoji cues and confidence scores

### Classification Categories
- **Momentum Long (🟢):** Crypto rallies with strong BTC and Gold confirmation and shallow drawdowns
- **Momentum Short (🔴):** Crypto sells off while diverging from Bitcoin leadership
- **Uncorrelated Hold (⚪):** Asset is moving independently of macro drivers
- **High Volatility (🟠):** Elevated risk from volatility or excessive BTC beta
- **Macro Divergence (🟣):** Bitcoin and Gold disagree, highlighting potential regime shifts
- **Caution (🟡):** Mixed signals that warrant monitoring but not immediate action

### Model Features
- 60-day rolling correlations versus Bitcoin, Gold, the S&P 500, and the U.S. Dollar Index
- Annualised 14-day volatility and 30-day maximum drawdown
- 14-day momentum and dynamic BTC beta exposure
- Bitcoin ↔ Gold alignment tracker for macro regime interpretation
- Continuous signal-strength score to rank conviction across assets

## Project Structure

```
The-Backward-7evin/
├── README.md                           # Project documentation
├── requirements.txt                    # Python dependencies
├── backward7evin_classifier.py         # Main classifier (80-100 lines) - PRIMARY SUBMISSION
├── backward7evin_predictor.py          # Advanced predictor with Random Forest
├── dashboard.py                        # Streamlit visualization dashboard
├── data/                               # Offline sample dataset bundle
│   ├── README.md                       # Snapshot provenance
│   └── market_history_sample.csv       # 210-day aligned market history
└── docs/
    └── Unit2_Summary.docx             # 1-page APA report with screenshots
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Run Main Classifier (Rubric Submission)
```bash
python backward7evin_classifier.py
```

The console output is rendered with the `rich` library: expect colour-coded tables, spotlight panels, and a narrative summary of the current Bitcoin ↔ Gold relationship.

### Run Advanced Predictor
```bash
python backward7evin_predictor.py
```

### Launch Dashboard
```bash
streamlit run dashboard.py
```

## Rubric Compliance (125 Points)

| Component | Requirements | Implementation | Points |
|-----------|--------------|----------------|--------|
| **Python Application** | 80-100 lines, well-commented | `backward7evin_classifier.py` | 30 |
| **Dataset** | Appropriate dataset selected | Yahoo Finance macro + crypto data | 30 |
| **Machine Learning** | Supervised learning demonstration | Interpretable rule-based classifier | 30 |
| **Organization** | Logical presentation | Modular code, clear documentation | 25 |
| **Professional Language** | APA formatting, no errors | `Unit2_Summary.docx` | 10 |
| **Total** | | | **125** |

## Results Summary

Each run produces:
- A dashboard-quality terminal report with emoji-labelled signals and confidence scores
- Spotlight highlights for top momentum leaders and the strongest Bitcoin-vs-Gold divergences
- A saved CSV (`crypto_signals_output.csv`) for documentation or further modelling
- A macro narrative explaining whether Gold is confirming or hedging current Bitcoin moves

## Academic Integrity

This project was developed for educational purposes as part of CS379 Machine Learning coursework. All data sources are properly cited and comply with fair use policies.

## License

Educational use only - CS379 Unit 2 Individual Project

## Author

Joey Bolkovatz
Colorado Technical University
October 2025
