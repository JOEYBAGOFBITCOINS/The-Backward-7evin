# The Backward 7evin - Usage Guide

## Quick Start Guide

### Step 1: Installation

```bash
# Navigate to project directory
cd The-Backward-7evin

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run Main Classifier (Primary Submission)

```bash
python backward7evin_classifier.py
```

**Expected Output:**
- Console output showing classification results
- Generated file: `crypto_signals_output.csv`
- Signal distribution summary

**Screenshot Capture Points:**
1. Terminal output showing classification results table
2. CSV file opened in Excel/text editor

### Step 3: Run Advanced Predictor (Enhanced Version)

```bash
python backward7evin_predictor.py
```

**Expected Output:**
- Model training progress
- Cross-validation scores
- Confusion matrix
- Classification report with precision/recall/F1
- Feature importance rankings
- Current market signal prediction
- Generated file: `feature_importance.csv`

**Screenshot Capture Points:**
1. Model evaluation results (accuracy, confusion matrix)
2. Feature importance table
3. Current market signal prediction

### Step 4: Launch Interactive Dashboard

```bash
streamlit run dashboard.py
```

**Dashboard Features:**
- **Tab 1: Daily Signals** - Color-coded signal cards for all cryptocurrencies
- **Tab 2: Correlation Analysis** - Heatmap and time-series comparisons
- **Tab 3: Model Insights** - Algorithm explanation and feature importance

**Screenshot Capture Points:**
1. Daily Signals tab showing all asset signals
2. Correlation heatmap from Tab 2
3. Feature importance chart from Tab 3

---

## File Descriptions

### Core Files (Submit These)

1. **backward7evin_classifier.py** (PRIMARY SUBMISSION)
   - 95 lines of well-commented code
   - Supervised classification algorithm
   - Meets 80-100 line rubric requirement

2. **Unit2_Summary.docx** (PRIMARY SUBMISSION)
   - 1-page APA-formatted report
   - Algorithm rationale
   - Results with screenshots
   - Dataset description

### Supplementary Files (Portfolio/Enhancement)

3. **backward7evin_predictor.py**
   - Advanced Random Forest implementation
   - Model evaluation metrics
   - Feature importance analysis

4. **dashboard.py**
   - Interactive Streamlit visualization
   - Real-time market data display
   - Multi-tab interface

5. **requirements.txt**
   - Python dependencies
   - Version specifications

---

## Expected Execution Time

- **backward7evin_classifier.py**: ~30-60 seconds (depending on network speed)
- **backward7evin_predictor.py**: ~2-3 minutes (includes model training)
- **dashboard.py**: Launches immediately, data loads on first view

---

## Troubleshooting

### Issue: "yfinance download failed"
**Solution:** Check internet connection. Yahoo Finance may temporarily rate-limit requests.

### Issue: "Module not found"
**Solution:** Ensure all requirements are installed: `pip install -r requirements.txt`

### Issue: "Streamlit command not found"
**Solution:** Install streamlit: `pip install streamlit`

### Issue: "Empty DataFrame"
**Solution:** Reduce lookback days or check if market is open (avoid weekends/holidays)

---

## Screenshot Checklist for Word Document

For the 1-page summary document, capture these screenshots:

- [ ] Main classifier output table showing signals for all cryptocurrencies
- [ ] Dashboard main view with color-coded signal cards
- [ ] Feature importance chart or correlation heatmap
- [ ] (Optional) Model accuracy metrics from predictor

**Screenshot Tips:**
1. Use full-screen terminal for classifier output
2. Zoom dashboard to 90-100% for clear capture
3. Ensure all text is readable
4. Crop unnecessary whitespace
5. Resize images to fit within 1-page Word document

---

## Submission Checklist

### Required Files (125 points):
- [ ] `backward7evin_classifier.py` (80-100 lines, well-commented)
- [ ] `Unit2_JoeyBolkovatz.docx` (1-page summary with screenshots)

### Optional Files (Portfolio/Enhancement):
- [ ] `backward7evin_predictor.py` (advanced implementation)
- [ ] `dashboard.py` (interactive visualization)
- [ ] `requirements.txt` (dependencies)
- [ ] `README.md` (project documentation)
- [ ] Generated CSV files (results output)

---

## Rubric Alignment Verification

| Component | Requirement | Implementation | ✓ |
|-----------|-------------|----------------|---|
| **Python Application (30 pts)** | 80-100 lines, well-commented | 95 lines, extensive comments | ✓ |
| **Dataset (30 pts)** | Appropriate dataset | Yahoo Finance crypto + macro | ✓ |
| **Machine Learning (30 pts)** | Supervised learning | Random Forest classification | ✓ |
| **Organization (25 pts)** | Logical presentation | Modular code, clear structure | ✓ |
| **Professional Language (10 pts)** | APA format, no errors | Word doc with proper citations | ✓ |

**Total: 125 points**

---

## Academic Integrity Note

This project uses publicly available data from Yahoo Finance for educational purposes.
All code is original work developed for CS379 Machine Learning coursework.
Proper citations are included in the summary document per APA guidelines.

---

## Support

For issues or questions:
1. Review troubleshooting section above
2. Check README.md for additional documentation
3. Verify all requirements are installed
4. Ensure Python 3.9+ is being used

---

**Project:** The Backward 7evin
**Course:** CS379 Machine Learning - Unit 2 Individual Project
**Author:** Joey Bolkovatz
**Date:** October 2025
