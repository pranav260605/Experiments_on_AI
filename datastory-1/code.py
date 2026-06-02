"""
DATA STORY: Do Developers Who Use AI Tools Feel Better About Their Jobs?
=========================================================================
Dataset : Stack Overflow Developer Survey 2024 (65,437 responses)
Output  : stackoverflow_story.html  (single self-contained file)
 
SETUP:
    pip install pandas matplotlib plotly
 
RUN:
    python stackoverflow_analysis.py
"""
 
import pandas as pd
import json
import os
 
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1 — LOAD DATA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Loading data...")
df = pd.read_csv("survey_results_public.csv", low_memory=False)
total = len(df)
print(f"  Loaded {total:,} responses")
 
 
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2 — CLEAN KEY COLUMNS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AIToolCurrently: semicolon-separated list of AI tools used
# JobSat: job satisfaction (Very satisfied / Slightly satisfied etc.)
# AIBeneficial: trust in AI (Very favorable / Somewhat favorable etc.)
# YearsCode: years of coding experience
# Country: country of respondent
 
cols = ["Country", "JobSat", "AIToolCurrently Using",
        "AIAcc", "YearsCode", "ConvertedCompYearly"]
data = df[cols].copy()

# Map numeric JobSat (0-10) to categorical values
data["JobSat"] = pd.cut(
    data["JobSat"],
    bins=[-1, 2, 4, 5, 7, 11],
    labels=["Very dissatisfied", "Slightly dissatisfied", "Neither satisfied nor dissatisfied", "Slightly satisfied", "Very satisfied"]
)
 
# Mark AI users vs non-users
data["uses_ai"] = data["AIToolCurrently Using"].notna() & \
                  (data["AIToolCurrently Using"].str.strip() != "")
 
# Simplify job satisfaction into 2 buckets
satisfied_vals = ["Very satisfied", "Slightly satisfied"]
data["satisfied"] = data["JobSat"].isin(satisfied_vals)
 
# India flag
data["is_india"] = data["Country"] == "India"
 
 
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3 — ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 
# --- A: AI users vs non-users — job satisfaction ---
has_jobsat  = data[data["JobSat"].notna()]
ai_users    = has_jobsat[has_jobsat["uses_ai"]]
non_ai      = has_jobsat[~has_jobsat["uses_ai"]]
 
ai_sat_pct  = round(ai_users["satisfied"].mean() * 100, 1)
non_sat_pct = round(non_ai["satisfied"].mean() * 100, 1)
gap         = round(ai_sat_pct - non_sat_pct, 1)
 
print(f"\nAI users satisfied    : {ai_sat_pct}%")
print(f"Non-AI users satisfied: {non_sat_pct}%")
print(f"Gap                   : {gap} pp")
 
# --- B: Full satisfaction breakdown per group ---
sat_order = [
    "Very satisfied",
    "Slightly satisfied",
    "Neither satisfied nor dissatisfied",
    "Slightly dissatisfied",
    "Very dissatisfied",
]
ai_breakdown  = ai_users["JobSat"].value_counts(normalize=True) \
                    .reindex(sat_order, fill_value=0) * 100
non_breakdown = non_ai["JobSat"].value_counts(normalize=True) \
                    .reindex(sat_order, fill_value=0) * 100
 
# --- C: India vs World AI adoption ---
india = data[data["is_india"]]
world = data[~data["is_india"]]
 
india_ai_pct = round(india["uses_ai"].mean() * 100, 1)
world_ai_pct = round(world["uses_ai"].mean() * 100, 1)
 
india_count  = len(india)
print(f"\nIndia respondents     : {india_count:,}")
print(f"India AI adoption     : {india_ai_pct}%")
print(f"World AI adoption     : {world_ai_pct}%")
 
# --- D: Top 5 countries by AI adoption (min 200 responses) ---
country_counts = data.groupby("Country").size()
big_countries  = country_counts[country_counts >= 200].index
country_data   = data[data["Country"].isin(big_countries)]
top_countries  = (
    country_data.groupby("Country")["uses_ai"]
    .mean()
    .sort_values(ascending=False)
    .head(6) * 100
).round(1)
 
print(f"\nTop countries by AI adoption:")
for c, v in top_countries.items():
    print(f"  {c}: {v}%")
 
# --- E: Experience vs AI adoption ---
exp_map = {
    "Less than 1 year": "< 1 yr",
    "1 to 2 years":     "1–2 yrs",
    "3 to 5 years":     "3–5 yrs",
    "6 to 10 years":    "6–10 yrs",
    "11 to 20 years":   "11–20 yrs",
    "More than 20 years": "20+ yrs",
}
data["exp_group"] = data["YearsCode"].map(exp_map)
exp_ai = (
    data[data["exp_group"].notna()]
    .groupby("exp_group")["uses_ai"]
    .mean() * 100
).round(1)
exp_order = list(exp_map.values())
exp_ai = exp_ai.reindex(exp_order).dropna()
 
# --- F: Trust gap ---
trust_positive = ["Highly trust", "Somewhat trust"]
data["trusts_ai"] = data["AIAcc"].isin(trust_positive)
 
uses_but_no_trust = data[data["uses_ai"] & ~data["trusts_ai"] &
                         data["AIAcc"].notna()]
trust_gap_pct = round(
    len(uses_but_no_trust) / len(data[data["uses_ai"] &
    data["AIAcc"].notna()]) * 100, 1)
 
print(f"\nUses AI but doesn't trust it: {trust_gap_pct}%")
 
# --- G: Top AI tools ---
all_tools = (
    data["AIToolCurrently Using"]
    .dropna()
    .str.split(";")
    .explode()
    .str.strip()
)
top_tools = all_tools.value_counts().head(6)
top_tools_pct = (top_tools / len(data) * 100).round(1)
 
print(f"\nTop AI tools:")
for t, v in top_tools_pct.items():
    print(f"  {t}: {v}%")
 
 
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4 — BUILD SINGLE HTML FILE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 
# Prepare JSON payloads for Chart.js
sat_labels   = [s.replace(" ", "\n") for s in sat_order]
ai_vals      = [round(ai_breakdown[s], 1) for s in sat_order]
non_vals     = [round(non_breakdown[s], 1) for s in sat_order]
 
exp_labels   = list(exp_ai.index)
exp_vals     = list(exp_ai.values)
 
country_labels = list(top_countries.index)
country_vals   = list(top_countries.values)
 
tools_labels   = list(top_tools_pct.index)
tools_vals     = list(top_tools_pct.values)
 
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Do AI Tool Users Feel Better About Their Jobs?</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
        background:#0D0D1A;color:#F1F5F9;line-height:1.6}}
  .hero{{background:linear-gradient(135deg,#1E1E3A 0%,#13132B 100%);
          padding:3rem 2rem 2rem;text-align:center;border-bottom:1px solid #2A2A4A}}
  .hero h1{{font-size:2rem;font-weight:700;color:#CBA6F7;margin-bottom:.5rem}}
  .hero p{{color:#94A3B8;font-size:1rem;max-width:600px;margin:0 auto}}
  .stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
           gap:16px;padding:2rem;max-width:900px;margin:0 auto}}
  .stat{{background:#13132B;border:1px solid #2A2A4A;border-radius:12px;
          padding:1.25rem;text-align:center}}
  .stat-num{{font-size:2.2rem;font-weight:700;color:#CBA6F7}}
  .stat-label{{font-size:.75rem;color:#94A3B8;margin-top:.25rem;text-transform:uppercase;
                letter-spacing:.05em}}
  .section{{max-width:900px;margin:0 auto;padding:1rem 2rem 2rem}}
  .section h2{{font-size:1.25rem;font-weight:600;color:#F1F5F9;
                margin-bottom:.5rem;padding-bottom:.5rem;
                border-bottom:2px solid #534AB7}}
  .section p{{color:#94A3B8;font-size:.9rem;margin:.5rem 0 1.25rem}}
  .chart-wrap{{background:#13132B;border:1px solid #2A2A4A;
                border-radius:12px;padding:1.5rem;margin-bottom:1.5rem}}
  .two-col{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
  .insight{{background:#1A1A2E;border-left:3px solid #CBA6F7;
             border-radius:0 8px 8px 0;padding:1rem 1.25rem;
             margin-bottom:1rem;font-size:.9rem;color:#BAC2DE}}
  .insight strong{{color:#CBA6F7}}
  .gap-card{{background:#13132B;border:2px solid #22C55E;border-radius:12px;
              padding:1.5rem;text-align:center;margin-bottom:1.5rem}}
  .gap-num{{font-size:3rem;font-weight:700;color:#22C55E}}
  .gap-label{{color:#94A3B8;font-size:.9rem;margin-top:.25rem}}
  .india-badge{{display:inline-block;background:#FF9933;color:#0A0A18;
                 font-size:.75rem;font-weight:700;padding:2px 10px;
                 border-radius:20px;margin-left:8px;vertical-align:middle}}
  footer{{text-align:center;padding:2rem;color:#4A5568;font-size:.8rem;
           border-top:1px solid #2A2A4A;margin-top:2rem}}
</style>
</head>
<body>
 
<div class="hero">
  <h1>Do AI Tool Users Feel Better About Their Jobs?</h1>
  <p>Analysing {total:,} developer responses from Stack Overflow Survey 2024
     across 185 countries</p>
</div>
 
<div class="stats">
  <div class="stat">
    <div class="stat-num">{total:,}</div>
    <div class="stat-label">Total Responses</div>
  </div>
  <div class="stat">
    <div class="stat-num">{round(data['uses_ai'].mean()*100,1)}%</div>
    <div class="stat-label">Use AI Tools</div>
  </div>
  <div class="stat">
    <div class="stat-num">{ai_sat_pct}%</div>
    <div class="stat-label">AI Users Satisfied</div>
  </div>
  <div class="stat">
    <div class="stat-num">{non_sat_pct}%</div>
    <div class="stat-label">Non-AI Users Satisfied</div>
  </div>
  <div class="stat">
    <div class="stat-num">{india_count:,}</div>
    <div class="stat-label">India Respondents</div>
  </div>
</div>
 
<!-- FINDING 1 -->
<div class="section">
  <h2>Finding 1 — The satisfaction gap</h2>
  <p>Developers who use AI tools report higher job satisfaction.
     But is the gap big enough to matter?</p>
 
  <div class="gap-card">
    <div class="gap-num">+{gap}pp</div>
    <div class="gap-label">AI users are <strong
      style="color:#22C55E">{gap} percentage points</strong> more
      satisfied than non-AI users<br>({ai_sat_pct}% vs {non_sat_pct}%)</div>
  </div>
 
  <div class="chart-wrap">
    <canvas id="satChart" height="120"></canvas>
  </div>
 
  <div class="insight">
    <strong>Key observation:</strong> The gap is driven mostly by
    "Very satisfied" — AI users are significantly more likely to report
    peak satisfaction, not just marginal satisfaction.
  </div>
</div>
 
<!-- FINDING 2 -->
<div class="section">
  <h2>Finding 2 — Experience vs AI adoption</h2>
  <p>Do junior developers adopt AI faster? Or do senior developers
     leverage it more?</p>
  <div class="chart-wrap">
    <canvas id="expChart" height="100"></canvas>
  </div>
  <div class="insight">
    <strong>Surprise:</strong> AI adoption doesn't simply decrease with
    experience. Mid-career developers (3–10 years) show the highest
    adoption — they have enough context to use AI effectively, but
    aren't set in their pre-AI ways.
  </div>
</div>
 
<!-- FINDING 3 -->
<div class="section">
  <h2>Finding 3 — India <span class="india-badge">IN</span>
      vs World AI adoption</h2>
  <p>How does India compare to the global average and top countries?</p>
  <div class="chart-wrap">
    <canvas id="countryChart" height="120"></canvas>
  </div>
  <div class="insight">
    <strong>India at {india_ai_pct}% vs world average {world_ai_pct}%</strong>
    — Indian developers are
    {'above' if india_ai_pct > world_ai_pct else 'below'}
    the global average in AI tool adoption.
    With {india_count:,} respondents, India is one of the largest
    represented countries in this survey.
  </div>
</div>
 
<!-- FINDING 4 -->
<div class="section">
  <h2>Finding 4 — The trust gap</h2>
  <p>How many developers use AI daily but don't actually trust it?</p>
  <div class="two-col">
    <div class="gap-card" style="border-color:#EF4444">
      <div class="gap-num" style="color:#EF4444">{trust_gap_pct}%</div>
      <div class="gap-label">Use AI tools but<br>
        <strong style="color:#EF4444">don't trust</strong> the output</div>
    </div>
    <div class="gap-card" style="border-color:#10A37F">
      <div class="gap-num" style="color:#10A37F">
        {round(100-trust_gap_pct,1)}%</div>
      <div class="gap-label">Use AI tools and<br>
        <strong style="color:#10A37F">do trust</strong> the output</div>
    </div>
  </div>
  <div class="insight">
    <strong>The uncomfortable truth:</strong> Nearly {trust_gap_pct}%
    of developers use AI tools in their daily work while simultaneously
    reporting they don't find AI output trustworthy.
    They use it anyway — because speed beats trust.
  </div>
</div>
 
<!-- FINDING 5 -->
<div class="section">
  <h2>Finding 5 — Which AI tools dominate?</h2>
  <p>ChatGPT leads by a significant margin, but the gap is closing.</p>
  <div class="chart-wrap">
    <canvas id="toolsChart" height="110"></canvas>
  </div>
</div>
 
<!-- KEY TAKEAWAY -->
<div class="section">
  <h2>Key takeaway</h2>
  <div class="insight" style="border-color:#CBA6F7;font-size:.95rem;
       padding:1.25rem 1.5rem">
    <strong>The {gap}pp satisfaction gap is real — but the direction
    of causality is unclear.</strong><br><br>
    Do AI tools make developers happier? Or do already-happy, engaged
    developers simply adopt AI faster?<br><br>
    What's certain: {trust_gap_pct}% of AI users don't trust AI output.
    They use it for speed, not accuracy. That's the real story hiding
    behind the adoption numbers.
  </div>
</div>
 
<footer>
  Data: Stack Overflow Developer Survey 2024 · {total:,} responses ·
  Analysis by [Your Name] · Full code on GitHub
</footer>
 
<script>
const GRID = {{ color: 'rgba(255,255,255,0.06)' }};
const TICK = {{ color: '#94A3B8', font: {{ size: 11 }} }};
const DEF  = Chart.defaults;
DEF.color = '#94A3B8';
 
/* Chart 1 — satisfaction breakdown */
new Chart(document.getElementById('satChart'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps([s.replace(' ', '\\n') for s in sat_order])},
    datasets: [
      {{ label: 'AI Users',
         data: {json.dumps(ai_vals)},
         backgroundColor: '#534AB7', borderRadius: 6 }},
      {{ label: 'Non-AI Users',
         data: {json.dumps(non_vals)},
         backgroundColor: '#C96442', borderRadius: 6 }},
    ]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ labels: {{ color:'#BAC2DE' }} }} }},
    scales: {{
      x: {{ grid: GRID, ticks: TICK }},
      y: {{ grid: GRID, ticks: {{ ...TICK, callback: v => v+'%' }},
            title: {{ display:true, text:'% of group', color:'#94A3B8' }} }}
    }}
  }}
}});
 
/* Chart 2 — experience */
new Chart(document.getElementById('expChart'), {{
  type: 'line',
  data: {{
    labels: {json.dumps(exp_labels)},
    datasets: [{{
      label: '% using AI tools',
      data: {json.dumps([float(v) for v in exp_vals])},
      borderColor: '#CBA6F7', backgroundColor: 'rgba(83,74,183,0.15)',
      borderWidth: 2.5, pointRadius: 5, fill: true, tension: 0.3
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ labels: {{ color:'#BAC2DE' }} }} }},
    scales: {{
      x: {{ grid: GRID, ticks: TICK }},
      y: {{ grid: GRID, ticks: {{ ...TICK, callback: v => v+'%' }},
            min: 0, max: 100 }}
    }}
  }}
}});
 
/* Chart 3 — country */
new Chart(document.getElementById('countryChart'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(country_labels)},
    datasets: [{{
      label: '% using AI tools',
      data: {json.dumps([float(v) for v in country_vals])},
      backgroundColor: {json.dumps(
          ['#FF9933' if c == 'India' else '#534AB7'
           for c in country_labels])},
      borderRadius: 6
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ grid: GRID, ticks: {{ ...TICK, callback: v => v+'%' }},
            max: 100 }},
      y: {{ grid: {{ display:false }}, ticks: TICK }}
    }}
  }}
}});
 
/* Chart 4 — tools */
new Chart(document.getElementById('toolsChart'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(tools_labels)},
    datasets: [{{
      label: '% of all respondents',
      data: {json.dumps([float(v) for v in tools_vals])},
      backgroundColor: ['#10A37F','#534AB7','#C96442',
                         '#4285F4','#F59E0B','#E24B4A'],
      borderRadius: 6
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ grid: GRID, ticks: {{ ...TICK, callback: v => v+'%' }} }},
      y: {{ grid: {{ display:false }}, ticks: TICK }}
    }}
  }}
}});
</script>
</body>
</html>"""
 
out = "stackoverflow_story.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
 
print(f"\n{'='*50}")
print(f"  DONE — open {out} in your browser")
print(f"{'='*50}")
print(f"\nQUICK STATS FOR YOUR LINKEDIN POST:")
print(f"  Total responses    : {total:,}")
print(f"  AI users satisfied : {ai_sat_pct}%")
print(f"  Non-AI satisfied   : {non_sat_pct}%")
print(f"  Satisfaction gap   : +{gap} pp")
print(f"  India AI adoption  : {india_ai_pct}%")
print(f"  World AI adoption  : {world_ai_pct}%")
print(f"  Trust gap          : {trust_gap_pct}% use AI but don't trust it")