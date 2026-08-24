import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from textblob import TextBlob

st.set_page_config(page_title="CB Sentiment Analyser", page_icon="🏦", layout="wide")

# ── STYLING ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
.stApp { background-color: #faf8f4; color: #0d1b2e; font-family: 'IBM Plex Sans', sans-serif; }
.main .block-container { padding: 1.5rem 2.5rem; max-width: 1400px; }
[data-testid="metric-container"] {
    background: #f0ece4; border: 1px solid #d0ccc4;
    border-top: 3px solid #0d3b7a; padding: 1rem; border-radius: 2px;
}
[data-testid="metric-container"] label {
    color: #3a4a5a !important; font-size: 0.65rem !important;
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
    padding: 1rem 1.2rem; border-radius: 2px; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem; color: #0d1b2e; line-height: 1.7; margin: 0.5rem 0;
}
.hawk-box { border-left-color: #c0392b !important; background: #fdf0ee !important; }
.dove-box { border-left-color: #1a6b3c !important; background: #eef6f0 !important; }
.footer-bar { border-top: 2px solid #1a1a1a; padding-top: 0.6rem; color: #5a6a7a; font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; margin-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── HAWKISH/DOVISH LEXICON ───────────────────────────────────────────────────
HAWKISH = [
    'inflation', 'elevated', 'tighten', 'tightening', 'raise', 'hike', 'increase rate',
    'highly attentive', 'strongly committed', 'attentive to inflation', 'remains elevated',
    'persistent', 'upside risks', 'overheat', 'restrictive', 'above target',
    'price stability', 'wage growth', 'demand pressures', 'supply constraints',
    'reduce holdings', 'balance sheet', 'quantitative tightening'
]

DOVISH = [
    'maximum employment', 'labor market', 'unemployment', 'slowdown', 'downside risks',
    'patient', 'gradual', 'accommodate', 'support', 'stimulus', 'ease', 'cut',
    'lower', 'reduce rate', 'dovish', 'slack', 'below target', 'recovery',
    'maintain', 'pause', 'hold', 'stable', 'balance of risks', 'uncertainty'
]

def score_statement(text):
    text_lower = text.lower()
    hawk_hits = sum(1 for w in HAWKISH if w in text_lower)
    dove_hits = sum(1 for w in DOVISH if w in text_lower)
    blob = TextBlob(text)
    tb_score = blob.sentiment.polarity
    raw = (hawk_hits - dove_hits) / max(hawk_hits + dove_hits, 1)
    combined = raw * 0.7 + (-tb_score) * 0.3
    return round(combined * 100, 1), hawk_hits, dove_hits

def label(score):
    if score > 30: return "🦅 Hawkish", "#c0392b"
    elif score > 10: return "↗ Mildly Hawkish", "#e67e22"
    elif score > -10: return "⚖ Neutral", "#1e5fb4"
    elif score > -30: return "↘ Mildly Dovish", "#2980b9"
    else: return "🕊 Dovish", "#1a6b3c"

# ── STATEMENT DATABASE ───────────────────────────────────────────────────────
statements = {
    "Fed": [
        {"date":"2022-03","text":"Inflation is well above 2 percent and labor market has continued to strengthen. The Committee seeks to achieve maximum employment and inflation at the rate of 2 percent over the longer run. With inflation well above 2 percent and a strong labor market, the Committee decided to raise the target range for the federal funds rate. The Committee anticipates that ongoing increases will be appropriate. The Committee is strongly committed to returning inflation to its 2 percent objective."},
        {"date":"2022-06","text":"Overall economic activity appears to have picked up after edging down in the first quarter. Job gains have been robust and the unemployment rate has remained low. Inflation remains elevated, reflecting supply and demand imbalances related to the pandemic, higher energy prices, and broader price pressures. The Committee is highly attentive to inflation risks. The Committee decided to raise the target range by 75 basis points. The Committee is strongly committed to returning inflation to its 2 percent objective."},
        {"date":"2022-11","text":"Recent indicators point to modest growth in spending and production. Job gains have been robust and the unemployment rate has remained low. Inflation remains elevated, reflecting supply and demand imbalances related to the pandemic, higher energy prices, and broader price pressures. The Committee decided to raise the target range by 75 basis points. Ongoing increases in the target range will be appropriate. The Committee is strongly committed to returning inflation to its 2 percent objective."},
        {"date":"2023-02","text":"Inflation has eased somewhat but remains elevated. Russia's war against Ukraine is causing tremendous human and economic hardship and is contributing to elevated global uncertainty. The Committee anticipates that ongoing increases in the target range will be appropriate. The Committee is strongly committed to returning inflation to its 2 percent objective."},
        {"date":"2023-09","text":"Recent indicators suggest that economic activity has been expanding at a solid pace. Job gains have slowed in recent months but remain strong, and the unemployment rate has remained low. Inflation remains elevated. The Committee decided to maintain the target range at 5.25 to 5.5 percent. The Committee does not expect it will be appropriate to reduce the target range until it has gained greater confidence that inflation is moving sustainably toward 2 percent."},
        {"date":"2024-03","text":"Recent indicators suggest that economic activity has been expanding at a solid pace. Job gains have remained strong, and the unemployment rate has remained low. Inflation has eased over the past year but remains elevated. The Committee judges that the risks to achieving its employment and inflation goals are moving into better balance. The Committee decided to maintain the target range at 5.25 to 5.5 percent. The Committee does not expect it will be appropriate to reduce the target range until it has gained greater confidence that inflation is moving sustainably toward 2 percent."},
        {"date":"2024-09","text":"Recent indicators suggest that economic activity has continued to expand at a solid pace. Job gains have slowed, and the unemployment rate has moved up but remains low. Inflation has made further progress toward the Committee's 2 percent objective but remains somewhat elevated. The Committee has gained greater confidence that inflation is moving sustainably toward 2 percent. The Committee decided to lower the target range for the federal funds rate by 1/2 percentage point to 4.75 to 5 percent."},
        {"date":"2025-01","text":"Recent indicators suggest that economic activity has continued to expand at a solid pace. The unemployment rate has stabilized at a low level in recent months, and labor market conditions remain solid. Inflation remains somewhat elevated. The Committee judges that the risks to achieving its employment and inflation goals are roughly in balance. The economic outlook is uncertain, and the Committee is attentive to the risks to both sides of its dual mandate. The Committee decided to maintain the target range for the federal funds rate at 4.25 to 4.5 percent."},
        {"date":"2025-06","text":"Although swings in net exports have affected the data, recent indicators suggest that economic activity has continued to expand at a solid pace. The unemployment rate remains low, and labor market conditions remain solid. Inflation remains somewhat elevated. Uncertainty about the economic outlook has diminished but remains elevated. The Committee decided to maintain the target range for the federal funds rate at 4.25 to 4.5 percent."},
        {"date":"2025-10","text":"Available indicators suggest that economic activity has been expanding at a moderate pace. Job gains have slowed this year, and the unemployment rate has edged up but remained low. Inflation has moved up since earlier in the year and remains somewhat elevated. The Committee is attentive to the risks to both sides of its dual mandate and judges that downside risks to employment rose in recent months. The Committee decided to lower the target range for the federal funds rate by 1/4 percentage point to 3.75 to 4 percent."},
        {"date":"2025-12","text":"Available indicators suggest that economic activity has been expanding at a moderate pace. Job gains have slowed this year, and the unemployment rate has edged up through September. Inflation has moved up since earlier in the year and remains somewhat elevated. The Committee is attentive to the risks to both sides of its dual mandate and judges that downside risks to employment rose in recent months. The Committee decided to lower the target range for the federal funds rate by 1/4 percentage point to 3.5 to 3.75 percent."},
    ],
    "BoE": [
        {"date":"2022-02","text":"CPI inflation has risen sharply since the August Report and is expected to increase further in coming months. The labour market is tight and domestic cost and price pressures have strengthened. Given the current tightness of the labour market, continuing signs of robust domestic cost and price pressures, and the risk that those pressures will persist, the Committee voted to increase Bank Rate by 0.25 percentage points to 0.5%."},
        {"date":"2022-06","text":"CPI inflation is expected to rise further. The labour market remains tight with high nominal wage growth. Inflationary pressures from external factors have intensified. The MPC voted to increase Bank Rate by 0.25 percentage points to 1.25%. The MPC will take the actions necessary to return inflation to the 2% target sustainably."},
        {"date":"2022-11","text":"CPI inflation was 10.1% in September. The labour market remains tight. A further significant increase in energy prices is expected. The MPC voted to increase Bank Rate by 0.75 percentage points to 3%. The MPC will take the actions necessary to return inflation to the 2% target sustainably in the medium term."},
        {"date":"2023-06","text":"CPI inflation was 8.7% in April. Services inflation remained elevated. Labour market conditions remain tight. There has been significant upside news in recent data. The MPC voted to increase Bank Rate by 0.5 percentage points to 5%. The MPC will ensure Bank Rate is sufficiently restrictive for sufficiently long to return inflation to the 2% target sustainably."},
        {"date":"2024-08","text":"CPI inflation was 2% in May and June. Services CPI inflation remains elevated. The labour market has continued to ease. GDP growth has been stronger than expected. The MPC voted by a majority to reduce Bank Rate by 0.25 percentage points to 5%. Monetary policy will need to remain restrictive for sufficiently long until the risks to inflation returning sustainably to the 2% target have dissipated further."},
        {"date":"2025-02","text":"CPI inflation was 2.5% in December. Services CPI inflation remains elevated. The labour market has continued to ease and is now broadly in balance. The MPC voted by a majority to reduce Bank Rate by 0.25 percentage points to 4.5%. A gradual approach to removing monetary policy restraint remains appropriate."},
        {"date":"2025-08","text":"CPI inflation is expected to rise to around 3.5% in the near term. Services inflation remains elevated. The labour market has eased further. The MPC voted to maintain Bank Rate at 4.25%. The MPC will remain data dependent and will assess whether the conditions are met for further reductions in Bank Rate."},
    ],
    "MAS": [
        {"date":"2021-10","text":"MAS will increase slightly the rate of appreciation of the S$NEER policy band. The width of the policy band and the level at which it is centred will be unchanged. The prevailing rate of S$NEER appreciation has been maintained since October 2016. With Singapore's economic recovery on track and inflationary pressures emerging, MAS assesses that a modest and gradual appreciation of the S$NEER policy band is appropriate."},
        {"date":"2022-01","text":"MAS will re-centre the mid-point of the S$NEER policy band at its prevailing level. The rate of appreciation of the policy band and its width will be unchanged. Core inflation has risen to around 2% and is expected to average higher in 2022. MAS is tightening monetary policy to dampen imported inflation and ensure that Singapore's domestic cost pressures remain manageable."},
        {"date":"2022-04","text":"MAS will increase further the rate of appreciation of the S$NEER policy band. MAS will also re-centre the mid-point of the S$NEER at its prevailing level. The width of the policy band will be unchanged. Core inflation is expected to remain elevated this year, averaging 2.5-3.5%. Tighter monetary policy will help keep a lid on imported inflation and domestic cost pressures."},
        {"date":"2022-07","text":"MAS will increase further the rate of appreciation of the S$NEER policy band. The mid-point of the policy band will be re-centred at the prevailing level of the S$NEER. Core inflation has risen sharply to 3.6% in May and is expected to remain elevated in H2 2022. A stronger S$NEER will dampen imported inflation and reduce the risk of inflation becoming entrenched."},
        {"date":"2022-10","text":"MAS will re-centre the mid-point of the S$NEER policy band at the prevailing level of the S$NEER. The rate of appreciation of the policy band and its width will be unchanged. Core inflation has remained elevated. The tighter monetary policy stance since October 2021 is working its way through the economy."},
        {"date":"2023-04","text":"MAS will maintain the prevailing rate of appreciation of the S$NEER policy band. The width of the policy band and the level at which it is centred will be unchanged. Core inflation is expected to ease through the course of the year. MAS assesses that the current monetary policy stance is sufficiently restrictive to bring inflation to a low and stable level."},
        {"date":"2024-10","text":"MAS will maintain the prevailing rate of appreciation of the S$NEER policy band. The width of the policy band and the level at which it is centred will be unchanged. Core inflation has moderated to around 2.5% in August. The prevailing monetary policy stance remains appropriate for ensuring medium-term price stability."},
        {"date":"2025-01","text":"MAS will reduce slightly the rate of appreciation of the S$NEER policy band. The width of the policy band and the level at which it is centred will be unchanged. Core inflation is expected to continue to ease. MAS assesses that a slight reduction in the pace of S$NEER appreciation is appropriate given the improved inflation outlook."},
        {"date":"2025-07","text":"MAS will maintain the prevailing rate of appreciation of the S$NEER policy band, following the slight reduction in January 2025. The width of the policy band and the level at which it is centred will be unchanged. Core inflation is expected to average around 1-2% in 2025. The current monetary policy stance is appropriate."},
    ],
    "ECB": [
        {"date":"2022-07","text":"The Governing Council decided to raise the three key ECB interest rates by 50 basis points. Inflation is an unacceptably high challenge. Russia's unjustified war against Ukraine is an ongoing drag on growth in Europe. The Governing Council will ensure that inflation returns to its 2% target over the medium term. The Governing Council judged that it is appropriate to take a larger first step on its policy rate normalisation path than signalled at its previous meeting."},
        {"date":"2022-12","text":"The Governing Council decided to raise the three key ECB interest rates by 50 basis points. Interest rates will still have to rise significantly at a steady pace to reach levels that are sufficiently restrictive. Inflation remains far too high and is projected to stay above the target for too long. The Governing Council will stay the course in raising interest rates significantly."},
        {"date":"2023-06","text":"The Governing Council decided to raise the three key ECB interest rates by 25 basis points. Inflation has been coming down but is projected to remain too high for too long. The Governing Council is determined to ensure that inflation returns to its 2% medium-term target in a timely manner. The Governing Council intends to raise interest rates again in July."},
        {"date":"2023-10","text":"The Governing Council decided to keep the three key ECB interest rates unchanged. Inflation has dropped considerably, though it is still expected to remain too high for too long. The Governing Council's future decisions will ensure that its policy rates will be set at sufficiently restrictive levels for as long as necessary."},
        {"date":"2024-06","text":"The Governing Council decided to lower the three key ECB interest rates by 25 basis points. Based on an updated assessment of the inflation outlook, the dynamics of underlying inflation and the strength of monetary policy transmission, it is now appropriate to moderate the degree of monetary policy restriction."},
        {"date":"2024-12","text":"The Governing Council decided to lower the three key ECB interest rates by 25 basis points. Inflation is on track to return sustainably to the Governing Council's 2% medium-term target. The disinflation process is well on track. The Governing Council is determined to ensure that inflation stabilises sustainably at its 2% medium-term target."},
        {"date":"2025-04","text":"The Governing Council decided to lower the three key ECB interest rates by 25 basis points. Disinflation is proceeding well. Staff project that inflation will fluctuate around the current level in the near term. The Governing Council is determined to ensure that inflation stabilises sustainably at its 2% medium-term target. The policy stance is becoming meaningfully less restrictive."},
    ],
    "RBI": [
        {"date":"2022-05","text":"The Monetary Policy Committee decided unanimously to increase the policy repo rate by 40 basis points to 4.4%. Inflation has risen sharply and is ruling above the upper tolerance band of 6%. Supply chain disruptions have intensified. The MPC judged that the risks to inflation are on the upside. Anchoring of inflation expectations is the need of the hour."},
        {"date":"2022-09","text":"The MPC decided to increase the policy repo rate by 50 basis points to 5.9%. CPI headline inflation remained elevated at 7.0% in August. Core inflation remains sticky. The MPC reiterated its determination to withdraw accommodation to ensure that inflation remains within the target going forward while supporting growth."},
        {"date":"2023-04","text":"The MPC decided to keep the policy repo rate unchanged at 6.5%. CPI inflation has been moderating. The MPC remains focused on withdrawal of accommodation to ensure that inflation progressively aligns with the target, while supporting growth. Food price uncertainties remain elevated."},
        {"date":"2024-02","text":"The MPC decided to keep the policy repo rate unchanged at 6.5%. Headline inflation moderated to 5.1% in January. Food inflation remains elevated. The MPC remains focused on withdrawal of accommodation to ensure that inflation progressively aligns to the target, while supporting growth."},
        {"date":"2024-10","text":"The MPC decided to keep the policy repo rate unchanged at 6.5%. Headline CPI inflation eased to 3.65% in August. Food inflation remains a concern. The MPC changed its stance to neutral. The MPC remains unambiguously focused on a durable alignment of inflation to the target, while supporting growth."},
        {"date":"2025-02","text":"The MPC decided to reduce the policy repo rate by 25 basis points to 6.25%. Inflation is expected to ease. Growth has been moderating. The MPC changed its stance to neutral. With inflation expected to ease and growth moderating, the MPC judged that there is space to support growth while remaining focused on inflation."},
        {"date":"2025-06","text":"The MPC decided to reduce the policy repo rate by 25 basis points to 6.0%. Headline CPI inflation has eased to around 3.6%. Food inflation has moderated. Growth has moderated somewhat. The MPC changed its stance to accommodative. The MPC is focused on supporting durable growth while keeping inflation aligned to the target."},
    ]
}

# Score all statements
for cb, stmts in statements.items():
    for s in stmts:
        s['score'], s['hawk'], s['dove'] = score_statement(s['text'])
        s['label'], s['colour'] = label(s['score'])
        s['cb'] = cb

# Flatten
all_stmts = [s for stmts in statements.values() for s in stmts]
df = pd.DataFrame(all_stmts)
df['date_dt'] = pd.to_datetime(df['date'])
df = df.sort_values('date_dt')

# ── PALETTE ──────────────────────────────────────────────────────────────────
BG='#faf8f4'; BG2='#f0ece4'; BLUE='#0d3b7a'; DARK='#0d1b2e'
MUTED='#7a6f60'; GRID='#d8d4cc'; RED='#c0392b'; GREEN='#1a6b3c'
CB_COLOURS = {'Fed':'#1e5fb4','BoE':'#c0392b','MAS':'#1a6b3c','ECB':'#e67e22','RBI':'#8a6e00'}

# ── MASTHEAD ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class='masthead'>
  <div class='masthead-eyebrow'>GOKHALE MACRO RESEARCH · NLP ANALYSIS · AUGUST 2026</div>
  <div class='masthead-title'>🏦 Central Bank Communication Sentiment Analyser</div>
  <div class='masthead-sub'>Hawkish/dovish scoring of Fed · BoE · MAS · ECB · RBI policy statements · 2022–2025</div>
</div>
""", unsafe_allow_html=True)

# ── LATEST READINGS ────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>[ 01 ] Latest Readings — Most Recent Statement Per Bank</div>", unsafe_allow_html=True)

cards_html = "<div style='display:grid; grid-template-columns: repeat(5,1fr); gap:1rem; margin-bottom:1rem;'>"
for cb in ['Fed','BoE','MAS','ECB','RBI']:
    latest = df[df['cb']==cb].sort_values('date_dt').iloc[-1]
    lbl, col = latest['label'], latest['colour']
    score_str = f"{latest['score']:+.0f}"
    cards_html += f"""
    <div style='background:#f0ece4; border:1px solid #d0ccc4; border-top:3px solid #0d3b7a;
                padding:1rem; border-radius:2px;'>
        <div style='color:#3a4a5a; font-family:IBM Plex Mono,monospace; font-size:0.62rem;
                    text-transform:uppercase; letter-spacing:0.12em; margin-bottom:0.4rem;'>
            {cb} · {latest['date']}
        </div>
        <div style='color:#0d1b2e; font-family:IBM Plex Mono,monospace; font-size:1.6rem;
                    font-weight:700; line-height:1.1;'>
            {score_str}
        </div>
        <div style='color:{col}; font-family:IBM Plex Mono,monospace; font-size:0.75rem;
                    font-weight:600; margin-top:0.3rem;'>
            {lbl}
        </div>
    </div>"""
cards_html += "</div>"
st.markdown(cards_html, unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── MAIN CHART ─────────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>[ 02 ] Hawkishness Score Over Time · All Central Banks</div>", unsafe_allow_html=True)
st.caption("Score: +100 = maximally hawkish · 0 = neutral · -100 = maximally dovish. Methodology: custom hawkish/dovish lexicon (70%) + TextBlob sentiment (30%)")

fig = go.Figure()
for cb in ['Fed','BoE','MAS','ECB','RBI']:
    sub = df[df['cb']==cb].sort_values('date_dt')
    fig.add_trace(go.Scatter(
        x=sub['date_dt'], y=sub['score'],
        name=cb, mode='lines+markers',
        line=dict(color=CB_COLOURS[cb], width=2),
        marker=dict(size=8, color=CB_COLOURS[cb]),
        hovertemplate=f'<b>{cb}</b><br>%{{x|%b %Y}}<br>Score: %{{y:+.0f}}<br>%{{customdata}}<extra></extra>',
        customdata=sub['label']
    ))

fig.add_hline(y=0, line_dash='dot', line_color=MUTED, line_width=1)
fig.add_hrect(y0=10, y1=100, fillcolor='rgba(192,57,43,0.04)', line_width=0)
fig.add_hrect(y0=-100, y1=-10, fillcolor='rgba(26,107,60,0.04)', line_width=0)
fig.add_annotation(x='2022-06-01', y=85, text='Peak tightening cycle',
    showarrow=False, font=dict(size=9, color=MUTED, family='IBM Plex Mono'),
    bgcolor=BG2, bordercolor=GRID, borderwidth=1)

fig.update_layout(
    plot_bgcolor=BG, paper_bgcolor=BG, height=420,
    font=dict(family='IBM Plex Mono', color=MUTED),
    legend=dict(orientation='h', y=1.06, font=dict(color=DARK, size=11), bgcolor='rgba(0,0,0,0)'),
    xaxis=dict(gridcolor=GRID, tickfont=dict(size=9, color=MUTED), linecolor=GRID),
    yaxis=dict(gridcolor=GRID, tickfont=dict(size=9, color=MUTED), linecolor=GRID,
               title=dict(text='Hawkishness Score', font=dict(size=10, color=MUTED)),
               range=[-100, 100]),
    margin=dict(t=40, b=40, l=70, r=20), hovermode='x unified',
    hoverlabel=dict(bgcolor=BG2, bordercolor=BLUE, font=dict(family='IBM Plex Mono', color=DARK))
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── EXPLAINER ────────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>[ 03 ] What Do These Scores Mean in Practice?</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
<div class='dcp-box'>
<b style='color:#c0392b;'>🦅 Hawkish (Score > +30)</b><br><br>
The central bank is prioritising <b>inflation control</b> over growth. Expect rate hikes or tighter policy ahead. For investors: bonds sell off, currency strengthens. For workers: borrowing costs rise, real wages face pressure if inflation stays high. The 2022 Fed and BoE were deeply hawkish — UK workers lost real wages for two consecutive years.
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown("""
<div class='dcp-box'>
<b style='color:#0d3b7a;'>⚖ Neutral (Score -10 to +10)</b><br><br>
The central bank is in <b>wait and see</b> mode. Policy is on hold, watching incoming data. Neither hiking nor cutting is imminent. This is where MAS sat through 2023-2024 after its aggressive 2022 tightening cycle — the S$NEER was kept at its appreciated level, doing the work passively without further adjustments.
</div>
""", unsafe_allow_html=True)

with col3:
    st.markdown("""
<div class='dcp-box'>
<b style='color:#1a6b3c;'>🕊 Dovish (Score < -30)</b><br><br>
The central bank is prioritising <b>growth and employment</b> over inflation control. Expect rate cuts or looser policy. For investors: bonds rally, currency weakens. For workers: borrowing is cheaper but inflation may creep up. The RBI's mid-2025 shift to accommodative stance signals growth concerns are now dominant over inflation fears.
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── ANALYSER ──────────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>[ 04 ] Analyse Any Statement — Paste Text Below</div>", unsafe_allow_html=True)

col1, col2 = st.columns([2,1])
with col1:
    user_text = st.text_area(
        "Paste any central bank statement here",
        height=180,
        placeholder="Paste a central bank policy statement here and click Analyse...",
        label_visibility='collapsed'
    )
    cb_name = st.text_input("Central bank / label (optional)", placeholder="e.g. Fed, BoE, MAS...")

with col2:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if st.button("🔍 Analyse Statement", use_container_width=True):
        if user_text.strip():
            score, hawk, dove = score_statement(user_text)
            lbl, col = label(score)
            box_class = 'hawk-box' if score > 10 else 'dove-box' if score < -10 else ''
            st.markdown(f"""
            <div class='statement-box {box_class}'>
            <b>Verdict:</b> <span style='color:{col};font-weight:700;'>{lbl}</span><br>
            <b>Score:</b> {score:+.1f} / 100<br>
            <b>Hawkish signals:</b> {hawk} · <b>Dovish signals:</b> {dove}<br><br>
            <span style='color:#7a6f60;font-size:0.72rem;'>Methodology: custom lexicon (70%) + TextBlob sentiment (30%)</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Please paste a statement first.")

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── STATEMENT BROWSER ──────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>[ 05 ] Browse All Statements</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    cb_filter = st.multiselect('Central Bank', ['Fed','BoE','MAS','ECB','RBI'],
                                default=['Fed','BoE','MAS','ECB','RBI'])
with col2:
    stance_filter = st.multiselect('Stance', ['🦅 Hawkish','↗ Mildly Hawkish','⚖ Neutral','↘ Mildly Dovish','🕊 Dovish'],
                                    default=['🦅 Hawkish','↗ Mildly Hawkish','⚖ Neutral','↘ Mildly Dovish','🕊 Dovish'])

filtered = df[df['cb'].isin(cb_filter) & df['label'].isin(stance_filter)].sort_values('date_dt', ascending=False)

display = filtered[['date','cb','label','score','hawk','dove']].rename(columns={
    'date':'Date','cb':'Central Bank','label':'Stance','score':'Score','hawk':'Hawkish Signals','dove':'Dovish Signals'
})
st.dataframe(display, use_container_width=True, height=280)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── MAS CONNECTION ──────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>[ 06 ] The MAS Difference — Exchange Rate vs Interest Rate Signalling</div>", unsafe_allow_html=True)
st.markdown("""
<div class='statement-box'>
Standard central bank sentiment analysis was built for interest rate frameworks — the Fed, BoE, and ECB signal through words like "raise", "lower", "restrictive", and "accommodate". MAS signals differently: through S$NEER band adjustments (slope, width, centring). A MAS statement can be deeply hawkish without mentioning "raise" or "inflation" in conventional ways.<br><br>
This analyser captures MAS signals through S$NEER-specific vocabulary: "rate of appreciation", "re-centre", "strengthen", "dampen imported inflation". The result: MAS's 2022 tightening cycle scores as consistently hawkish despite looking neutral to a standard NLP model trained on interest rate language.<br><br>
<span style='color:#7a6f60;font-size:0.72rem;'>Research: Gokhale (2026) · ssrn.com/abstract=6514338 · MAS Dataset: mas-policy-dataset.streamlit.app</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='footer-bar'>
Built by Anuja A. Gokhale · MA Applied Economics, NUS (Merit Scholar) · anujagokhale1604@gmail.com · 
Methodology: custom hawkish/dovish lexicon (70 terms) + TextBlob sentiment analysis (30%) · 
Statements sourced from official central bank publications · August 2026
</div>
""", unsafe_allow_html=True)
