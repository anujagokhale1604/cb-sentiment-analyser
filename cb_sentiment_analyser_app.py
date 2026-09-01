import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from textblob import TextBlob
import re

st.set_page_config(page_title="CB Sentiment Analyser", page_icon="🏦", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

.stApp { background-color: #faf8f4; color: #0d1b2e; font-family: 'IBM Plex Sans', sans-serif; }
.main .block-container { padding: 1.5rem 2.5rem; max-width: 1400px; }

div[data-testid="stMetric"] * { color: #0d1b2e !important; }
[data-testid="metric-container"] {
    background: #f0ece4; border: 1px solid #d0ccc4;
    border-top: 3px solid #0d3b7a; padding: 1rem; border-radius: 4px;
}
[data-testid="metric-container"] label {
    color: #3a4a5a !important; font-size: 0.62rem !important;
    text-transform: uppercase; letter-spacing: 0.12em;
    font-family: 'IBM Plex Mono', monospace !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #0d1b2e !important; font-size: 1.4rem !important;
    font-weight: 700; font-family: 'IBM Plex Mono', monospace !important;
}
.section-header {
    color: #0d3b7a; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.18em;
    border-bottom: 1px solid #d0ccc4; padding-bottom: 0.3rem; margin-bottom: 1rem;
}
.masthead { border-bottom: 3px solid #0d1b2e; padding-bottom: 1rem; margin-bottom: 1.5rem; }
.masthead-eyebrow { color: #0d3b7a; font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.2em; margin-bottom: 0.4rem; }
.masthead-title { color: #0d1b2e; font-family: 'IBM Plex Sans', sans-serif; font-size: 2rem; font-weight: 700; }
.masthead-sub { color: #3a4a5a; font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; margin-top: 0.3rem; }

.statement-box {
    background: #f0ece4; border: 1px solid #d0ccc4; border-left: 4px solid #0d3b7a;
    padding: 1.2rem 1.4rem; border-radius: 4px; font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.85rem; color: #0d1b2e; line-height: 1.8; margin: 0.5rem 0;
}
.hawk-box { border-left-color: #c0392b !important; background: #fdf5f4 !important; }
.dove-box { border-left-color: #1a6b3c !important; background: #f3faf5 !important; }

.sentence-hawk { background: #fde8e5; border-left: 3px solid #c0392b; padding: 0.4rem 0.7rem; margin: 0.3rem 0; border-radius: 2px; font-size: 0.82rem; color: #0d1b2e; }
.sentence-dove { background: #e8f5ec; border-left: 3px solid #1a6b3c; padding: 0.4rem 0.7rem; margin: 0.3rem 0; border-radius: 2px; font-size: 0.82rem; color: #0d1b2e; }
.sentence-neutral { background: #f0ece4; border-left: 3px solid #aaaaaa; padding: 0.4rem 0.7rem; margin: 0.3rem 0; border-radius: 2px; font-size: 0.82rem; color: #0d1b2e; }

.divergence-box {
    background: #fff8e8; border: 1px solid #f0c060; border-left: 4px solid #e67e22;
    padding: 1rem 1.2rem; border-radius: 4px; font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.85rem; color: #0d1b2e; line-height: 1.7;
}
.align-box {
    background: #e8f5ec; border: 1px solid #90c4a0; border-left: 4px solid #1a6b3c;
    padding: 1rem 1.2rem; border-radius: 4px; font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.85rem; color: #0d1b2e; line-height: 1.7;
}
.dcp-box {
    background: #e8eef7; border: 1px solid #b8c8df; border-left: 4px solid #0d3b7a;
    padding: 1.2rem 1.5rem; border-radius: 4px; font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.85rem; color: #0d1b2e; line-height: 1.8;
}
.hist-box {
    background: #f0ece4; border: 1px solid #d0ccc4;
    padding: 0.8rem 1rem; border-radius: 4px; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem; color: #0d1b2e; line-height: 1.6; margin-top: 0.8rem;
}
.stTextArea textarea,
.stTextArea > div > div > textarea,
div[data-baseweb="textarea"] textarea {
    background-color: #ffffff !important;
    color: #0d1b2e !important;
    border: 1.5px solid #b8c8df !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.88rem !important;
    -webkit-text-fill-color: #0d1b2e !important;
    caret-color: #0d1b2e !important;
}
div[data-baseweb="textarea"] { background-color: #ffffff !important; }
.stTextInput input {
    background-color: #ffffff !important;
    color: #0d1b2e !important;
    border: 1.5px solid #b8c8df !important;
    border-radius: 4px !important;
    -webkit-text-fill-color: #0d1b2e !important;
}
.stButton > button {
    background-color: #f0ece4 !important;
    color: #0d1b2e !important;
    border: 1.5px solid #0d3b7a !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    background-color: #0d3b7a !important;
    color: #ffffff !important;
}
.cb-links { display: flex; flex-wrap: wrap; gap: 0.6rem; margin-bottom: 1rem; }
.cb-link {
    background: #f0ece4; border: 1px solid #d0ccc4; border-radius: 3px;
    padding: 0.3rem 0.7rem; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem; color: #0d3b7a; text-decoration: none;
}
.footer-bar {
    border-top: 2px solid #0d1b2e; padding-top: 0.6rem; color: #5a6a7a;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── FINBERT WITH FALLBACK ─────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_finbert():
    try:
        from transformers import pipeline
        clf = pipeline('text-classification', model='ProsusAI/finbert', device=-1)
        return clf
    except Exception:
        return None

finbert = load_finbert()
USE_FINBERT = finbert is not None

# ── LEXICON ───────────────────────────────────────────────────────────────────
HAWKISH = [
    'inflation', 'elevated', 'tighten', 'tightening', 'raise', 'hike', 'increase rate',
    'highly attentive', 'strongly committed', 'attentive to inflation', 'remains elevated',
    'persistent', 'upside risks', 'overheat', 'restrictive', 'above target',
    'price stability', 'wage growth', 'demand pressures', 'supply constraints',
    'reduce holdings', 'balance sheet', 'quantitative tightening', 'rate of appreciation',
    'strengthen', 're-centre', 'tighter monetary', 'dampen imported inflation'
]
DOVISH = [
    'maximum employment', 'labor market', 'unemployment', 'slowdown', 'downside risks',
    'patient', 'gradual', 'accommodate', 'support', 'stimulus', 'ease', 'cut',
    'lower', 'reduce rate', 'dovish', 'slack', 'below target', 'recovery',
    'maintain', 'pause', 'hold', 'stable', 'balance of risks', 'uncertainty',
    'reduce slightly', 'accommodative', 'easing'
]

def lexicon_score(text):
    t = text.lower()
    hawk_hits = sum(1 for w in HAWKISH if w in t)
    dove_hits = sum(1 for w in DOVISH if w in t)
    blob = TextBlob(text)
    tb = blob.sentiment.polarity
    raw = (hawk_hits - dove_hits) / max(hawk_hits + dove_hits, 1)
    combined = raw * 0.7 + (-tb) * 0.3
    return round(combined * 100, 1), hawk_hits, dove_hits

def finbert_score_text(text):
    try:
        chunks = [text[i:i+400] for i in range(0, len(text), 400)]
        scores = []
        for chunk in chunks[:5]:
            result = finbert(chunk, truncation=True, max_length=512)[0]
            label_map = {'positive': -50, 'negative': 50, 'neutral': 0}
            scores.append(label_map.get(result['label'], 0) * result['score'])
        return round(np.mean(scores), 1)
    except:
        return None

def score_statement(text):
    lex, hawk, dove = lexicon_score(text)
    if USE_FINBERT:
        fb = finbert_score_text(text)
        if fb is not None:
            return round(lex * 0.5 + fb * 0.5, 1), hawk, dove
    return lex, hawk, dove

def label_fn(score):
    if score > 30:    return "🦅 Hawkish", "#c0392b"
    elif score > 10:  return "↗ Mildly Hawkish", "#e67e22"
    elif score > -10: return "⚖ Neutral", "#1e5fb4"
    elif score > -30: return "↘ Mildly Dovish", "#2980b9"
    else:             return "🕊 Dovish", "#1a6b3c"

def plain_english(score):
    if score > 30:
        return "Rates likely rising. Borrowing gets more expensive."
    elif score > 10:
        return "Leaning toward tighter policy. Rates expected to stay elevated — the bank is watching inflation closely before making a move."
    elif score > -10:
        return "On hold. The bank is watching incoming data carefully before committing to a direction."
    elif score > -30:
        return "Leaning toward easier policy. Rate cuts are being considered — borrowing costs may fall in coming months."
    else:
        return "Rates likely falling. The bank is prioritising growth. Borrowing gets cheaper."

# ── STATEMENT DATABASE ────────────────────────────────────────────────────────
statements = {
    "Fed": [
        {"date":"2022-03","text":"Inflation is well above 2 percent and labor market has continued to strengthen. The Committee seeks to achieve maximum employment and inflation at the rate of 2 percent over the longer run. With inflation well above 2 percent and a strong labor market, the Committee decided to raise the target range for the federal funds rate. The Committee anticipates that ongoing increases will be appropriate. The Committee is strongly committed to returning inflation to its 2 percent objective."},
        {"date":"2022-06","text":"Overall economic activity appears to have picked up after edging down in the first quarter. Job gains have been robust and the unemployment rate has remained low. Inflation remains elevated, reflecting supply and demand imbalances related to the pandemic, higher energy prices, and broader price pressures. The Committee is highly attentive to inflation risks. The Committee decided to raise the target range by 75 basis points. The Committee is strongly committed to returning inflation to its 2 percent objective."},
        {"date":"2022-11","text":"Recent indicators point to modest growth in spending and production. Job gains have been robust and the unemployment rate has remained low. Inflation remains elevated, reflecting supply and demand imbalances related to the pandemic, higher energy prices, and broader price pressures. The Committee decided to raise the target range by 75 basis points. Ongoing increases in the target range will be appropriate. The Committee is strongly committed to returning inflation to its 2 percent objective."},
        {"date":"2023-02","text":"Inflation has eased somewhat but remains elevated. Russia's war against Ukraine is causing tremendous human and economic hardship and is contributing to elevated global uncertainty. The Committee anticipates that ongoing increases in the target range will be appropriate. The Committee is strongly committed to returning inflation to its 2 percent objective."},
        {"date":"2023-09","text":"Recent indicators suggest that economic activity has been expanding at a solid pace. Job gains have slowed in recent months but remain strong, and the unemployment rate has remained low. Inflation remains elevated. The Committee decided to maintain the target range at 5.25 to 5.5 percent. The Committee does not expect it will be appropriate to reduce the target range until it has gained greater confidence that inflation is moving sustainably toward 2 percent."},
        {"date":"2024-03","text":"Recent indicators suggest that economic activity has been expanding at a solid pace. Job gains have remained strong, and the unemployment rate has remained low. Inflation has eased over the past year but remains elevated. The Committee judges that the risks to achieving its employment and inflation goals are moving into better balance. The Committee decided to maintain the target range at 5.25 to 5.5 percent."},
        {"date":"2024-09","text":"Recent indicators suggest that economic activity has continued to expand at a solid pace. Job gains have slowed, and the unemployment rate has moved up but remains low. Inflation has made further progress toward the Committee's 2 percent objective but remains somewhat elevated. The Committee decided to lower the target range for the federal funds rate by 1/2 percentage point to 4.75 to 5 percent."},
        {"date":"2025-01","text":"Recent indicators suggest that economic activity has continued to expand at a solid pace. The unemployment rate has stabilized at a low level in recent months, and labor market conditions remain solid. Inflation remains somewhat elevated. The Committee decided to maintain the target range for the federal funds rate at 4.25 to 4.5 percent."},
        {"date":"2025-06","text":"Although swings in net exports have affected the data, recent indicators suggest that economic activity has continued to expand at a solid pace. The unemployment rate remains low, and labor market conditions remain solid. Inflation remains somewhat elevated. The Committee decided to maintain the target range for the federal funds rate at 4.25 to 4.5 percent."},
        {"date":"2025-10","text":"Available indicators suggest that economic activity has been expanding at a moderate pace. Job gains have slowed this year, and the unemployment rate has edged up but remained low. Inflation has moved up since earlier in the year and remains somewhat elevated. The Committee decided to lower the target range for the federal funds rate by 1/4 percentage point to 3.75 to 4 percent."},
        {"date":"2025-12","text":"Available indicators suggest that economic activity has been expanding at a moderate pace. Job gains have slowed this year, and the unemployment rate has edged up through September. Inflation has moved up since earlier in the year and remains somewhat elevated. The Committee decided to lower the target range for the federal funds rate by 1/4 percentage point to 3.5 to 3.75 percent."},
    ],
    "BoE": [
        {"date":"2022-02","text":"CPI inflation has risen sharply since the August Report and is expected to increase further in coming months. The labour market is tight and domestic cost and price pressures have strengthened. Given the current tightness of the labour market, continuing signs of robust domestic cost and price pressures, and the risk that those pressures will persist, the Committee voted to increase Bank Rate by 0.25 percentage points to 0.5%."},
        {"date":"2022-06","text":"CPI inflation is expected to rise further. The labour market remains tight with high nominal wage growth. Inflationary pressures from external factors have intensified. The MPC voted to increase Bank Rate by 0.25 percentage points to 1.25%. The MPC will take the actions necessary to return inflation to the 2% target sustainably."},
        {"date":"2022-11","text":"CPI inflation was 10.1% in September. The labour market remains tight. A further significant increase in energy prices is expected. The MPC voted to increase Bank Rate by 0.75 percentage points to 3%. The MPC will take the actions necessary to return inflation to the 2% target sustainably in the medium term."},
        {"date":"2023-06","text":"CPI inflation was 8.7% in April. Services inflation remained elevated. Labour market conditions remain tight. There has been significant upside news in recent data. The MPC voted to increase Bank Rate by 0.5 percentage points to 5%. The MPC will ensure Bank Rate is sufficiently restrictive for sufficiently long to return inflation to the 2% target sustainably."},
        {"date":"2024-08","text":"CPI inflation was 2% in May and June. Services CPI inflation remains elevated. The labour market has continued to ease. GDP growth has been stronger than expected. The MPC voted by a majority to reduce Bank Rate by 0.25 percentage points to 5%. Monetary policy will need to remain restrictive for sufficiently long."},
        {"date":"2025-02","text":"CPI inflation was 2.5% in December. Services CPI inflation remains elevated. The labour market has continued to ease and is now broadly in balance. The MPC voted by a majority to reduce Bank Rate by 0.25 percentage points to 4.5%. A gradual approach to removing monetary policy restraint remains appropriate."},
        {"date":"2025-08","text":"CPI inflation is expected to rise to around 3.5% in the near term. Services inflation remains elevated. The labour market has eased further. The MPC voted to maintain Bank Rate at 4.25%. The MPC will remain data dependent and will assess whether the conditions are met for further reductions in Bank Rate."},
    ],
    "MAS": [
        {"date":"2021-10","text":"MAS will increase slightly the rate of appreciation of the S$NEER policy band. The width of the policy band and the level at which it is centred will be unchanged. With Singapore's economic recovery on track and inflationary pressures emerging, MAS assesses that a modest and gradual appreciation of the S$NEER policy band is appropriate."},
        {"date":"2022-01","text":"MAS will re-centre the mid-point of the S$NEER policy band at its prevailing level. Core inflation has risen to around 2% and is expected to average higher in 2022. MAS is tightening monetary policy to dampen imported inflation and ensure that Singapore's domestic cost pressures remain manageable."},
        {"date":"2022-04","text":"MAS will increase further the rate of appreciation of the S$NEER policy band. MAS will also re-centre the mid-point of the S$NEER at its prevailing level. Core inflation is expected to remain elevated this year, averaging 2.5-3.5%. Tighter monetary policy will help keep a lid on imported inflation and domestic cost pressures."},
        {"date":"2022-07","text":"MAS will increase further the rate of appreciation of the S$NEER policy band. Core inflation has risen sharply to 3.6% in May and is expected to remain elevated in H2 2022. A stronger S$NEER will dampen imported inflation and reduce the risk of inflation becoming entrenched."},
        {"date":"2022-10","text":"MAS will re-centre the mid-point of the S$NEER policy band at the prevailing level of the S$NEER. Core inflation has remained elevated. The tighter monetary policy stance since October 2021 is working its way through the economy."},
        {"date":"2023-04","text":"MAS will maintain the prevailing rate of appreciation of the S$NEER policy band. Core inflation is expected to ease through the course of the year. MAS assesses that the current monetary policy stance is sufficiently restrictive to bring inflation to a low and stable level."},
        {"date":"2024-10","text":"MAS will maintain the prevailing rate of appreciation of the S$NEER policy band. Core inflation has moderated to around 2.5% in August. The prevailing monetary policy stance remains appropriate for ensuring medium-term price stability."},
        {"date":"2025-01","text":"MAS will reduce slightly the rate of appreciation of the S$NEER policy band. Core inflation is expected to continue to ease. MAS assesses that a slight reduction in the pace of S$NEER appreciation is appropriate given the improved inflation outlook."},
        {"date":"2025-07","text":"MAS will maintain the prevailing rate of appreciation of the S$NEER policy band, following the slight reduction in January 2025. Core inflation is expected to average around 1-2% in 2025. The current monetary policy stance is appropriate."},
    ],
    "ECB": [
        {"date":"2022-07","text":"The Governing Council decided to raise the three key ECB interest rates by 50 basis points. Inflation is an unacceptably high challenge. The Governing Council will ensure that inflation returns to its 2% target over the medium term."},
        {"date":"2022-12","text":"The Governing Council decided to raise the three key ECB interest rates by 50 basis points. Interest rates will still have to rise significantly at a steady pace to reach levels that are sufficiently restrictive. Inflation remains far too high and is projected to stay above the target for too long."},
        {"date":"2023-06","text":"The Governing Council decided to raise the three key ECB interest rates by 25 basis points. Inflation has been coming down but is projected to remain too high for too long. The Governing Council is determined to ensure that inflation returns to its 2% medium-term target in a timely manner."},
        {"date":"2023-10","text":"The Governing Council decided to keep the three key ECB interest rates unchanged. Inflation has dropped considerably, though it is still expected to remain too high for too long."},
        {"date":"2024-06","text":"The Governing Council decided to lower the three key ECB interest rates by 25 basis points. It is now appropriate to moderate the degree of monetary policy restriction."},
        {"date":"2024-12","text":"The Governing Council decided to lower the three key ECB interest rates by 25 basis points. Inflation is on track to return sustainably to the Governing Council's 2% medium-term target. The disinflation process is well on track."},
        {"date":"2025-04","text":"The Governing Council decided to lower the three key ECB interest rates by 25 basis points. Disinflation is proceeding well. The policy stance is becoming meaningfully less restrictive."},
    ],
    "RBI": [
        {"date":"2022-05","text":"The Monetary Policy Committee decided unanimously to increase the policy repo rate by 40 basis points to 4.4%. Inflation has risen sharply and is ruling above the upper tolerance band of 6%. Anchoring of inflation expectations is the need of the hour."},
        {"date":"2022-09","text":"The MPC decided to increase the policy repo rate by 50 basis points to 5.9%. CPI headline inflation remained elevated at 7.0% in August. Core inflation remains sticky. The MPC reiterated its determination to withdraw accommodation to ensure that inflation remains within the target."},
        {"date":"2023-04","text":"The MPC decided to keep the policy repo rate unchanged at 6.5%. CPI inflation has been moderating. The MPC remains focused on withdrawal of accommodation to ensure that inflation progressively aligns with the target, while supporting growth."},
        {"date":"2024-02","text":"The MPC decided to keep the policy repo rate unchanged at 6.5%. Headline inflation moderated to 5.1% in January. Food inflation remains elevated. The MPC remains focused on withdrawal of accommodation."},
        {"date":"2024-10","text":"The MPC decided to keep the policy repo rate unchanged at 6.5%. Headline CPI inflation eased to 3.65% in August. The MPC changed its stance to neutral."},
        {"date":"2025-02","text":"The MPC decided to reduce the policy repo rate by 25 basis points to 6.25%. Inflation is expected to ease. Growth has been moderating. The MPC changed its stance to neutral."},
        {"date":"2025-06","text":"The MPC decided to reduce the policy repo rate by 25 basis points to 6.0%. Headline CPI inflation has eased to around 3.6%. The MPC changed its stance to accommodative."},
    ]
}

for cb, stmts in statements.items():
    for s in stmts:
        s['score'], s['hawk'], s['dove'] = score_statement(s['text'])
        s['label'], s['colour'] = label_fn(s['score'])
        s['cb'] = cb

all_stmts = [s for stmts in statements.values() for s in stmts]
df = pd.DataFrame(all_stmts)
df['date_dt'] = pd.to_datetime(df['date'])
df = df.sort_values('date_dt')

BG='#faf8f4'; BG2='#f0ece4'; NAVY='#0d3b7a'; DARK='#0d1b2e'; MUTED='#5a6a7a'; GRID='#d8d4cc'
CB_COLOURS = {'Fed':'#1e5fb4','BoE':'#c0392b','MAS':'#1a6b3c','ECB':'#e67e22','RBI':'#8a6e00'}

# ── MASTHEAD ──────────────────────────────────────────────────────────────────
model_label = 'FinBERT + Lexicon' if USE_FINBERT else 'Lexicon Model'
st.markdown(f"""
<div class='masthead'>
  <div class='masthead-eyebrow'>GOKHALE MACRO RESEARCH · NLP ANALYSIS · {model_label} · 2026</div>
  <div class='masthead-title'>🏦 Central Bank Communication Sentiment Analyser</div>
  <div class='masthead-sub'>Hawkish/dovish scoring of Fed · BoE · MAS · ECB · RBI policy statements · 2022–2025</div>
</div>
""", unsafe_allow_html=True)

# ── SECTION 01: LATEST READINGS ───────────────────────────────────────────────
st.markdown("<div class='section-header'>[ 01 ] Latest Readings — Most Recent Statement Per Bank</div>", unsafe_allow_html=True)

cards_html = "<div style='display:grid;grid-template-columns:repeat(5,1fr);gap:1rem;margin-bottom:1.5rem;'>"
for cb in ['Fed','BoE','MAS','ECB','RBI']:
    latest = df[df['cb']==cb].sort_values('date_dt').iloc[-1]
    lbl, col = latest['label'], latest['colour']
    cards_html += f"""
    <div style='background:#f0ece4;border:1px solid #d0ccc4;border-top:3px solid #0d3b7a;
                padding:1rem;border-radius:4px;'>
        <div style='color:#3a4a5a;font-family:IBM Plex Mono,monospace;font-size:0.62rem;
                    text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.4rem;'>
            {cb} · {latest['date']}
        </div>
        <div style='color:#0d1b2e;font-family:IBM Plex Mono,monospace;font-size:1.6rem;
                    font-weight:700;line-height:1.1;'>
            {latest['score']:+.0f}
        </div>
        <div style='color:{col};font-family:IBM Plex Mono,monospace;font-size:0.75rem;
                    font-weight:600;margin-top:0.3rem;'>
            {lbl}
        </div>
    </div>"""
cards_html += "</div>"
st.markdown(cards_html, unsafe_allow_html=True)

# ── SECTION 02: MAIN CHART ────────────────────────────────────────────────────
st.markdown("<div class='section-header'>[ 02 ] Hawkishness Score Over Time · All Central Banks</div>", unsafe_allow_html=True)
st.caption("Score: +100 = maximally hawkish · 0 = neutral · -100 = maximally dovish")

fig = go.Figure()
for cb in ['Fed','BoE','MAS','ECB','RBI']:
    sub = df[df['cb']==cb].sort_values('date_dt')
    fig.add_trace(go.Scatter(
        x=sub['date_dt'], y=sub['score'], name=cb, mode='lines+markers',
        line=dict(color=CB_COLOURS[cb], width=2), marker=dict(size=8, color=CB_COLOURS[cb]),
        hovertemplate=f'<b>{cb}</b><br>%{{x|%b %Y}}<br>Score: %{{y:+.0f}}<br>%{{customdata}}<extra></extra>',
        customdata=sub['label']
    ))
fig.add_hline(y=0, line_dash='dot', line_color=MUTED, line_width=1)
fig.add_hrect(y0=10, y1=100, fillcolor='rgba(192,57,43,0.04)', line_width=0)
fig.add_hrect(y0=-100, y1=-10, fillcolor='rgba(26,107,60,0.04)', line_width=0)
fig.update_layout(
    plot_bgcolor=BG, paper_bgcolor=BG, height=420,
    font=dict(family='IBM Plex Mono', color=MUTED),
    legend=dict(orientation='h', y=1.06, font=dict(color=DARK, size=11), bgcolor='rgba(0,0,0,0)'),
    xaxis=dict(gridcolor=GRID, tickfont=dict(size=9, color=MUTED), linecolor=GRID),
    yaxis=dict(gridcolor=GRID, tickfont=dict(size=9, color=MUTED), linecolor=GRID,
               title=dict(text='Hawkishness Score', font=dict(size=10, color=MUTED)), range=[-100,100]),
    margin=dict(t=40,b=40,l=70,r=20), hovermode='x unified',
    hoverlabel=dict(bgcolor=BG2, bordercolor=NAVY, font=dict(family='IBM Plex Mono', color=DARK))
)
st.plotly_chart(fig, use_container_width=True)

# ── SECTION 03: DIVERGENCE ALERT ─────────────────────────────────────────────
st.markdown("<div class='section-header'>[ 03 ] Cross-Bank Divergence Alert</div>", unsafe_allow_html=True)

latest_scores = {cb: df[df['cb']==cb].sort_values('date_dt').iloc[-1]['score'] for cb in ['Fed','BoE','MAS','ECB','RBI']}
max_cb = max(latest_scores, key=latest_scores.get)
min_cb = min(latest_scores, key=latest_scores.get)
divergence = latest_scores[max_cb] - latest_scores[min_cb]
max_lbl, max_col = label_fn(latest_scores[max_cb])
min_lbl, min_col = label_fn(latest_scores[min_cb])

if divergence > 40:
    st.markdown(f"""
<div class='divergence-box'>
<b>⚠️ Significant Policy Divergence Detected</b><br><br>
<b style='color:{max_col}'>{max_cb} ({max_lbl}, {latest_scores[max_cb]:+.0f})</b> and
<b style='color:{min_col}'>{min_cb} ({min_lbl}, {latest_scores[min_cb]:+.0f})</b> are moving in
opposite directions — a gap of {divergence:.0f} points. Diverging central bank stances typically
put pressure on exchange rates: the currency of the more hawkish central bank tends to appreciate
against the more dovish one. Capital tends to flow toward higher-yielding, tighter-policy economies.
</div>
""", unsafe_allow_html=True)
else:
    st.markdown(f"""
<div class='align-box'>
<b>✅ Central Banks Broadly Aligned</b><br><br>
The spread between the most hawkish (<b>{max_cb}, {latest_scores[max_cb]:+.0f}</b>) and most dovish
(<b>{min_cb}, {latest_scores[min_cb]:+.0f}</b>) central banks is {divergence:.0f} points — relatively
narrow. When major central banks move in sync, exchange rate pressure is limited and global
financial conditions tend to be more stable.
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

fig2 = go.Figure()
cbs_sorted = sorted(latest_scores.keys(), key=lambda x: latest_scores[x], reverse=True)
fig2.add_trace(go.Bar(
    x=cbs_sorted,
    y=[latest_scores[cb] for cb in cbs_sorted],
    marker_color=[CB_COLOURS[cb] for cb in cbs_sorted],
    text=[f"{latest_scores[cb]:+.0f}" for cb in cbs_sorted],
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>Score: %{y:+.0f}<extra></extra>'
))
fig2.add_hline(y=0, line_dash='dot', line_color=MUTED, line_width=1)
fig2.update_layout(
    plot_bgcolor=BG, paper_bgcolor=BG, height=260,
    font=dict(family='IBM Plex Mono', color=MUTED),
    xaxis=dict(gridcolor=GRID, tickfont=dict(size=11, color=DARK)),
    yaxis=dict(gridcolor=GRID, tickfont=dict(size=9, color=MUTED), range=[-100,100],
               title=dict(text='Hawkishness Score', font=dict(size=10, color=MUTED))),
    margin=dict(t=20,b=30,l=60,r=20), showlegend=False
)
st.plotly_chart(fig2, use_container_width=True)

# ── SECTION 04: WHAT DO SCORES MEAN ──────────────────────────────────────────
st.markdown("<div class='section-header'>[ 04 ] What Do These Scores Mean in Practice?</div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""<div class='dcp-box'>
<b style='color:#c0392b;'>🦅 Hawkish (Score &gt; +30)</b><br><br>
The central bank is prioritising <b>inflation control</b> over growth. Expect rate hikes or elevated rates ahead. For workers: borrowing costs rise, real wages face pressure. The 2022 Fed and BoE were deeply hawkish — UK workers lost real wages for two consecutive years.
</div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div class='dcp-box'>
<b style='color:#0d3b7a;'>⚖ Neutral (Score -10 to +10)</b><br><br>
The central bank is in <b>wait and see</b> mode. Policy is on hold, watching incoming data. Neither hiking nor cutting is imminent. MAS sat here through 2023–2024 — keeping its tightened stance passively without further adjustments.
</div>""", unsafe_allow_html=True)
with col3:
    st.markdown("""<div class='dcp-box'>
<b style='color:#1a6b3c;'>🕊 Dovish (Score &lt; -30)</b><br><br>
The central bank is prioritising <b>growth and employment</b>. Expect rate cuts or looser policy. For workers: borrowing is cheaper but inflation may creep up. The RBI's mid-2025 shift to accommodative stance signals growth concerns now dominate.
</div>""", unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── SECTION 05: ANALYSE ───────────────────────────────────────────────────────
st.markdown("<div class='section-header'>[ 05 ] Analyse Any Statement — Paste Text Below</div>", unsafe_allow_html=True)

st.markdown("""
<p style='font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#3a4a5a;margin-bottom:0.5rem;'>
Find official statements here:
</p>
<div class='cb-links'>
  <a class='cb-link' href='https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm' target='_blank'>🇺🇸 Fed FOMC</a>
  <a class='cb-link' href='https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes' target='_blank'>🇬🇧 BoE MPC</a>
  <a class='cb-link' href='https://www.mas.gov.sg/monetary-policy/monetary-policy-decisions' target='_blank'>🇸🇬 MAS</a>
  <a class='cb-link' href='https://www.ecb.europa.eu/press/pr/date/2025/html/index.en.html' target='_blank'>🇪🇺 ECB</a>
  <a class='cb-link' href='https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx' target='_blank'>🇮🇳 RBI</a>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2,1])
with col1:
    user_text = st.text_area(
        "Paste statement",
        height=200,
        placeholder="Copy and paste any central bank policy statement here, then click Analyse...",
        label_visibility='collapsed'
    )
    cb_name_input = st.text_input(
        "Central bank label (optional — for historical comparison)",
        placeholder="e.g. Fed, BoE, MAS, ECB, RBI..."
    )

with col2:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    analyse_clicked = st.button("🔍 Analyse Statement", use_container_width=True)

    if analyse_clicked:
        if user_text.strip():
            score, hawk, dove = score_statement(user_text)
            lbl, col = label_fn(score)
            box_class = 'hawk-box' if score > 10 else 'dove-box' if score < -10 else ''
            plain = plain_english(score)
            st.markdown(f"""
<div class='statement-box {box_class}'>
<b>Verdict:</b> <span style='color:{col};font-weight:700;'>{lbl}</span><br>
<b>Score:</b> {score:+.1f} / 100<br>
<b>Hawkish signals:</b> {hawk} · <b>Dovish signals:</b> {dove}
<div style='margin-top:0.7rem;padding-top:0.7rem;border-top:1px solid #d0ccc4;
            color:#0d1b2e;font-size:0.84rem;font-style:italic;font-weight:500;'>
{plain}
</div>
</div>
""", unsafe_allow_html=True)

            # Historical comparison
            cb_clean = cb_name_input.strip()
            if cb_clean and cb_clean in statements:
                cb_hist = df[df['cb']==cb_clean].sort_values('score', ascending=False).reset_index(drop=True)
                rank = int((cb_hist['score'] >= score).sum()) + 1
                total = len(cb_hist)
                most_hawk = cb_hist.iloc[0]
                most_dove = cb_hist.iloc[-1]
                st.markdown(f"""
<div class='hist-box'>
<b>Historical context ({cb_clean}):</b><br>
This statement ranks <b>#{rank} of {total}</b> by hawkishness.<br>
Most hawkish on record: {most_hawk['date']} ({most_hawk['score']:+.0f})<br>
Most dovish on record: {most_dove['date']} ({most_dove['score']:+.0f})
</div>
""", unsafe_allow_html=True)
        else:
            st.info("Paste a statement in the box on the left, then click Analyse.")

# ── SECTION 06: SENTENCE BREAKDOWN ───────────────────────────────────────────
if analyse_clicked and user_text.strip():
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>[ 06 ] Sentence-Level Breakdown — Which Lines Are Driving the Score</div>", unsafe_allow_html=True)

    sentences = [s.strip() for s in re.split(r'[.!?]+', user_text) if len(s.strip()) > 20]
    if sentences:
        html_parts = []
        for sent in sentences:
            s_score, _, _ = lexicon_score(sent)
            if s_score > 15:
                cls, icon = 'sentence-hawk', '🦅'
            elif s_score < -15:
                cls, icon = 'sentence-dove', '🕊'
            else:
                cls, icon = 'sentence-neutral', '—'
            html_parts.append(f"<div class='{cls}'>{icon}&nbsp;&nbsp;{sent}.</div>")
        st.markdown("\n".join(html_parts), unsafe_allow_html=True)
        st.caption("🦅 Red = hawkish · 🕊 Green = dovish · — Grey = neutral")

# ── SECTION 07: BROWSE ────────────────────────────────────────────────────────
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-header'>[ 07 ] Browse All Statements</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    cb_filter = st.multiselect('Central Bank', ['Fed','BoE','MAS','ECB','RBI'], default=['Fed','BoE','MAS','ECB','RBI'])
with col2:
    stance_filter = st.multiselect('Stance', ['🦅 Hawkish','↗ Mildly Hawkish','⚖ Neutral','↘ Mildly Dovish','🕊 Dovish'],
                                    default=['🦅 Hawkish','↗ Mildly Hawkish','⚖ Neutral','↘ Mildly Dovish','🕊 Dovish'])

filtered = df[df['cb'].isin(cb_filter) & df['label'].isin(stance_filter)].sort_values('date_dt', ascending=False)
display = filtered[['date','cb','label','score','hawk','dove']].rename(columns={
    'date':'Date','cb':'Central Bank','label':'Stance','score':'Score',
    'hawk':'Hawkish Signals','dove':'Dovish Signals'
})
st.dataframe(display, use_container_width=True, height=280)

# ── SECTION 08: MAS DIFFERENCE ────────────────────────────────────────────────
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-header'>[ 08 ] The MAS Difference — Exchange Rate vs Interest Rate Signalling</div>", unsafe_allow_html=True)
st.markdown("""
<div class='statement-box'>
Standard central bank sentiment analysis was built for interest rate frameworks. The Fed, BoE, and ECB signal through words like "raise", "lower", "restrictive", and "accommodate". MAS signals differently: through S$NEER band adjustments (slope, width, centring). A MAS statement can be deeply hawkish without mentioning "raise" or "inflation" in conventional ways.<br><br>
This analyser captures MAS signals through S$NEER-specific vocabulary: "rate of appreciation", "re-centre", "strengthen", "dampen imported inflation". The result: MAS's 2022 tightening cycle scores as consistently hawkish despite looking neutral to a standard NLP model trained on interest rate language.<br><br>
<span style='color:#5a6a7a;font-size:0.72rem;'>Research: Gokhale (2026) · ssrn.com/abstract=6514338 · MAS Dataset: mas-policy-dataset.streamlit.app</span>
</div>
""", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
model_str = 'FinBERT (ProsusAI) + Custom Lexicon' if USE_FINBERT else 'Custom Hawkish/Dovish Lexicon'
st.markdown(f"""
<div class='footer-bar'>
Built by Anuja A. Gokhale · MA Applied Economics, NUS (Merit Scholar) · anujagokhale1604@gmail.com ·
Model: {model_str} · Statements sourced from official central bank publications · 2026
</div>
""", unsafe_allow_html=True)
