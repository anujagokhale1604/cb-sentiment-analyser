# 🏦 Central Bank Communication Sentiment Analyser

**NLP-powered hawkish/dovish scoring of central bank policy statements across the Fed, BoE, MAS, ECB, and RBI (2022–2025).**

Built by [Anuja A. Gokhale](https://ssrn.com/author=10973290) (MA Applied Economics, NUS Merit Scholar) as a companion to research on monetary policy transmission and the S$NEER exchange rate framework.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cb-sentiment-analyser.streamlit.app)

---

## 🔍 What It Does

- **Scores** every major policy statement from five central banks on a hawkishness scale (-100 to +100)
- **Tracks** the tightening and easing cycle across banks on a single timeline
- **Analyses** any pasted statement in real time — paste text, get an instant verdict
- **Browses** all 41 scored statements with filterable stance and bank filters

---

## 🧠 Methodology

**Score = 0.7 × Lexicon Score + 0.3 × TextBlob Sentiment**

### Custom Hawkish/Dovish Lexicon

A 70-term lexicon built specifically for central bank communication:

**Hawkish signals include:** `inflation elevated`, `highly attentive`, `strongly committed`, `restrictive`, `raise`, `tighten`, `upside risks`, `reduce holdings`, `above target`, `wage growth`

**Dovish signals include:** `maximum employment`, `downside risks`, `patient`, `gradual`, `accommodate`, `ease`, `cut`, `maintain`, `pause`, `balance of risks`, `uncertainty`

### The MAS Problem

Standard NLP sentiment models were trained on interest rate language — the Fed, BoE, and ECB signal through words like "raise", "lower", and "restrictive". MAS signals differently: through S$NEER band adjustments (slope, width, centring).

This analyser captures MAS signals through S$NEER-specific vocabulary: `rate of appreciation`, `re-centre`, `strengthen`, `dampen imported inflation`, `policy band`. The result: MAS's 2022 tightening cycle scores as consistently hawkish despite looking neutral to a standard NLP model trained on interest rate language.

---

## 📊 Coverage

| Central Bank | Statements | Period |
|---|---|---|
| Federal Reserve (Fed) | 11 | Mar 2022 – Dec 2025 |
| Bank of England (BoE) | 7 | Feb 2022 – Aug 2025 |
| Monetary Authority of Singapore (MAS) | 9 | Oct 2021 – Jul 2025 |
| European Central Bank (ECB) | 7 | Jul 2022 – Apr 2025 |
| Reserve Bank of India (RBI) | 7 | May 2022 – Jun 2025 |

---

## 🔗 Research Connection

This tool extends the MAS Monetary Policy Stance Dataset ([mas-policy-dataset.streamlit.app](https://mas-policy-dataset.streamlit.app)) from classification-based scoring to NLP-based sentiment analysis.

The underlying research ([ssrn.com/abstract=6514338](https://ssrn.com/abstract=6514338)) documents that MAS's exchange rate tightening cycle absorbed the 2022 upstream inflation shock at the border — preserving Singapore workers' real wages while UK workers under BoE rate hikes experienced two consecutive years of negative real wage growth. The divergence in policy communication scores reflects this divergence in outcomes.

---

## 🚀 Run Locally

```bash
git clone https://github.com/anujagokhale1604/cb-sentiment-analyser
cd cb-sentiment-analyser
pip install -r requirements.txt
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
streamlit run app.py
```

---

## 📁 Files

| File | Description |
|---|---|
| `app.py` | Main Streamlit application |
| `requirements.txt` | Python dependencies |
| `packages.txt` | System-level packages for Streamlit Cloud |

---

## 📖 Citation

```
Gokhale, A.A. (2026). Central Bank Communication Sentiment Analyser [Tool].
GitHub. https://github.com/anujagokhale1604/cb-sentiment-analyser

Gokhale, A.A. (2026). Cross-Country Macroeconomic Dynamics: Inflation,
Growth, and Monetary Policy — India, Singapore, and the United Kingdom.
SSRN Working Paper. https://ssrn.com/abstract=6514338
```

---

## 📬 Contact

Anuja A. Gokhale · anujagokhale1604@gmail.com · [ssrn.com/author=10973290](https://ssrn.com/author=10973290)

---

*Statements sourced from official central bank publications. Methodology combines a custom domain-specific lexicon with TextBlob sentiment analysis. Built for research and educational purposes. Last updated August 2026.*
