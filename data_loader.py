import pandas as pd
import seaborn as sns
from math import pi
import plotly.io as pio
import os

pio.renderers.default = "browser"



# Load  IPL data 
df = pd.read_csv('data/raw/ipl_match_1473461_deliveries.csv')
df_copy = df.copy()
df
# add game phase based on overs
def get_phase(over):
    if over < 6:
        return 'Powerplay'
    elif 6 <= over < 15:
        return 'Middle Overs'
    else:
        return 'Death Overs'

df_copy['phase'] = df_copy['over'].apply(get_phase)

import plotly.express as px
import pandas as pd

batting_intent = (
    df_copy.groupby(['batter', 'phase'])
    .agg(balls_faced=('runs_batter', 'count'),
         total_runs=('runs_batter', 'sum'))
    .reset_index()
)
batting_intent['strike_rate'] = (batting_intent['total_runs'] / batting_intent['balls_faced']) * 100

batting_intent = batting_intent[batting_intent['balls_faced'] >= 5]

batting_intent.sort_values(by=['batter', 'phase'], inplace=True)

fig = px.bar(
    batting_intent,
    x='batter',
    y='strike_rate',
    color='phase',
    barmode='group',
    title='📊 Batting Intent: Strike Rate Across Phases of the Game',
    labels={'strike_rate': 'Strike Rate', 'batter': 'Batter'},
    hover_data={
        'balls_faced': True,
        'total_runs': True,
        'strike_rate': ':.2f',
        'phase': True
    }
)

fig.update_layout(
    xaxis_tickangle=-45,
    title_font_size=20,
    legend_title='Game Phase',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='white',
    bargap=0.2,
    margin=dict(l=40, r=40, t=80, b=100)
)

fig.update_traces(marker_line_width=1, marker_line_color='black')

fig.show()
df_copy['batting_team'] = df_copy['team']

team_phase_intent = (
    df_copy.groupby(['batting_team', 'phase'])
    .agg(balls_faced=('runs_batter', 'count'),
         total_runs=('runs_batter', 'sum'))
    .reset_index()
)

team_phase_intent['strike_rate'] = (team_phase_intent['total_runs'] / team_phase_intent['balls_faced']) * 100

fig = px.bar(
    team_phase_intent,
    x='phase',
    y='strike_rate',
    color='batting_team',
    barmode='group',
    title='🏏 Team-wise Batting Intent Across Match Phases',
    labels={
        'phase': 'Match Phase',
        'strike_rate': 'Strike Rate',
        'batting_team': 'Team'
    },
    hover_data={
        'balls_faced': True,
        'total_runs': True,
        'strike_rate': ':.2f'
    }
)

fig.update_layout(
    xaxis_title='Match Phase',
    yaxis_title='Strike Rate',
    title_font_size=20,
    legend_title_text='Batting Team',
    bargap=0.25,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='white',
    margin=dict(l=40, r=40, t=80, b=60)
)

fig.update_traces(marker_line_width=1, marker_line_color='black')

fig.show()
import plotly.graph_objects as go

df_copy['ball_outcome'] = df_copy['runs_batter'].apply(
    lambda x: 'Dot' if x == 0 else ('Boundary' if x >= 4 else 'Run')
)

batter_outcome_stats = (
    df_copy.groupby('batter')
    .ball_outcome.value_counts(normalize=True)
    .unstack()
    .fillna(0) * 100
).reset_index()

balls_faced = df_copy.groupby('batter').size().reset_index(name='balls_faced')
batter_outcome_stats = batter_outcome_stats.merge(balls_faced, on='batter')
batter_outcome_stats = batter_outcome_stats[batter_outcome_stats['balls_faced'] >= 10]

batter_outcome_stats = batter_outcome_stats.sort_values(by='Boundary', ascending=False)

fig = go.Figure()

fig.add_trace(go.Bar(
    x=batter_outcome_stats['batter'],
    y=batter_outcome_stats['Boundary'],
    name='Boundary %',
    marker_color='green',
    hovertemplate='%{x}<br>Boundary %: %{y:.2f}<extra></extra>'
))

fig.add_trace(go.Bar(
    x=batter_outcome_stats['batter'],
    y=batter_outcome_stats['Dot'],
    name='Dot Ball %',
    marker_color='red',
    hovertemplate='%{x}<br>Dot Ball %: %{y:.2f}<extra></extra>'
))

fig.update_layout(
    title='🏏 Boundary % vs Dot Ball % per Batter',
    xaxis_title='Batter',
    yaxis_title='Percentage (%)',
    barmode='group',
    bargap=0.25,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='white',
    legend_title_text='Ball Outcome',
    xaxis_tickangle=-45,
    margin=dict(l=40, r=40, t=80, b=100)
)
os.makedirs("results", exist_ok=True)  # Create folder if it doesn't exist
fig.write_image("results/boundarywise_analysis.png")  # Save as PNG
fig.write_html("results/boundarywise_analysis.html")  # Save interactive HTML

fig.show()
wickets_df = df_copy[df_copy['player_out'].notna()]
wickets_by_over = wickets_df.groupby('over').size().reset_index(name='wickets')

runs_by_over = df_copy.groupby('over')['runs_batter'].sum().reset_index(name='total_runs')

overwise_analysis = pd.merge(runs_by_over, wickets_by_over, on='over', how='left').fillna(0)

fig = go.Figure()

fig.add_trace(go.Bar(
    x=overwise_analysis['over'],
    y=overwise_analysis['total_runs'],
    name='Runs Scored',
    marker_color='skyblue',
    hovertemplate='Over %{x}<br>Runs: %{y}<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=overwise_analysis['over'],
    y=overwise_analysis['wickets'],
    name='Wickets',
    mode='lines+markers',
    marker=dict(color='red', size=8),
    line=dict(width=2, color='red'),
    yaxis='y2',
    hovertemplate='Over %{x}<br>Wickets: %{y}<extra></extra>'
))

fig.update_layout(
    title='📉 Over-wise Analysis: Runs vs Wickets',
    xaxis=dict(title='Over', tickmode='linear'),
    yaxis=dict(title='Runs Scored'),
    yaxis2=dict(title='Wickets', overlaying='y', side='right'),
    legend_title='Metrics',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='white',
    margin=dict(l=40, r=40, t=80, b=60),
    hovermode='x unified'
)

# ---------------- Save the plot in results/ folder ----------------
os.makedirs("results", exist_ok=True)  # Create folder if it doesn't exist
fig.write_image("results/overwise_analysis.png")  # Save as PNG
fig.write_html("results/overwise_analysis.html")  # Save interactive HTML

fig.show()
batter_stats = (
    df_copy.groupby('batter')
    .agg(
        balls_faced=('runs_batter', 'count'),
        total_runs=('runs_batter', 'sum'),
        dismissals=('player_out', lambda x: x.notna().sum())
    )
    .reset_index()
)

outcome_counts = df_copy.groupby(['batter', 'ball_outcome']).size().unstack().fillna(0)
outcome_counts['dot_percent'] = (outcome_counts['Dot'] / outcome_counts.sum(axis=1)) * 100
outcome_counts['boundary_percent'] = (outcome_counts['Boundary'] / outcome_counts.sum(axis=1)) * 100
outcome_counts = outcome_counts[['dot_percent', 'boundary_percent']].reset_index()

batter_profiles = pd.merge(batter_stats, outcome_counts, on='batter')
batter_profiles['strike_rate'] = (batter_profiles['total_runs'] / batter_profiles['balls_faced']) * 100
batter_profiles['average'] = batter_profiles.apply(
    lambda row: row['total_runs'] / row['dismissals'] if row['dismissals'] > 0 else float('inf'), axis=1
)
batter_profiles = batter_profiles[batter_profiles['balls_faced'] >= 10]
from plotly.subplots import make_subplots
from math import pi, ceil

metrics = ['strike_rate', 'dot_percent', 'boundary_percent']
top_batters_radar = batter_profiles.sort_values(by='strike_rate', ascending=False).head(4).copy()
normalized_profiles = top_batters_radar[['batter'] + metrics].copy()

for metric in metrics:
    max_val = batter_profiles[metric].max()
    normalized_profiles[metric] = (normalized_profiles[metric] / max_val) * 100

normalized_profiles.reset_index(drop=True, inplace=True)

num_batters = len(normalized_profiles)
rows = ceil(num_batters / 2)
cols = 2 if num_batters > 1 else 1

fig = make_subplots(
    rows=rows, cols=cols,
    specs=[[{'type': 'polar'}] * cols for _ in range(rows)],
    subplot_titles=normalized_profiles['batter'].tolist()
)

for i, row in normalized_profiles.iterrows():
    r = row[metrics].tolist() + [row[metrics[0]]]
    theta = metrics + [metrics[0]]

    subplot_row = (i // cols) + 1
    subplot_col = (i % cols) + 1

    fig.add_trace(
        go.Scatterpolar(
            r=r,
            theta=theta,
            fill='toself',
            name=row['batter'],
            hovertemplate='<b>%{theta}</b>: %{r:.1f}<extra></extra>'
        ),
        row=subplot_row, col=subplot_col
    )

fig.update_layout(
    title='🔘 Batter Profiles: Radar Chart of Batting Metrics',
    showlegend=False,
    height=400 * rows,
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)
    ),
    margin=dict(l=40, r=40, t=100, b=50)
)

# ---------------- Save the plot in results/ folder ----------------
os.makedirs("results", exist_ok=True)  # Create folder if it doesn't exist
fig.write_image("results/batterwise_analysis.png")  # Save as PNG
fig.write_html("results/batterwise_analysis.html")  # Save interactive HTML
fig.show()

