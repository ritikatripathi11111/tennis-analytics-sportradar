"""Reusable Plotly chart functions."""
"""Reusable Plotly chart builders with one consistent, recruiter-friendly style."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PALETTE = ["#16A34A", "#0EA5E9", "#F59E0B", "#8B5CF6", "#EF4444", "#14B8A6", "#64748B"]
GREENS = "Greens"


def _style(fig: go.Figure, title: str = "", height: int = 380) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)), height=height, template="plotly_white",
        margin=dict(l=10, r=10, t=55 if title else 15, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    return fig


def top_players_bar(df: pd.DataFrame, n: int = 10, title: str = "Top players by points") -> go.Figure:
    """Horizontal bar of the ``n`` highest-point players."""
    top = df.sort_values(["points", "rank"], ascending=[False, True]).head(n)
    fig = px.bar(top, x="points", y="name", orientation="h", text="points",
                 hover_data=["country", "rank"], color_discrete_sequence=[PALETTE[0]])
    fig.update_yaxes(categoryorder="total ascending", title="")
    fig.update_xaxes(title="Points")
    fig.update_traces(textposition="outside", cliponaxis=False)
    return _style(fig, title)


def country_choropleth(df: pd.DataFrame, value: str, title: str) -> go.Figure:
    """World map shaded by ``value`` (needs ISO-3 ``country_code``)."""
    fig = px.choropleth(df, locations="country_code", color=value, hover_name="country",
                        color_continuous_scale=GREENS)
    fig.update_geos(showframe=False, showcountries=True, countrycolor="#CBD5E1",
                    projection_type="natural earth")
    fig.update_layout(coloraxis_colorbar=dict(title="", thickness=12))
    return _style(fig, title, height=380)


def rank_points_scatter(df: pd.DataFrame, title: str = "Rank vs points (bubble = events played)") -> go.Figure:
    """Scatter of rank against points coloured by weekly movement."""
    fig = px.scatter(df, x="rank", y="points", size="competitions_played", color="movement",
                     hover_name="name", hover_data=["country"], size_max=16,
                     color_continuous_scale="RdYlGn", color_continuous_midpoint=0)
    fig.update_xaxes(title="Rank")
    fig.update_yaxes(title="Points")
    return _style(fig, title)


def movement_histogram(df: pd.DataFrame, title: str = "Weekly rank movement") -> go.Figure:
    """Distribution of rank movements."""
    fig = px.histogram(df, x="movement", nbins=25, color_discrete_sequence=[PALETTE[1]])
    fig.update_xaxes(title="Places moved (+ = up)")
    fig.update_yaxes(title="Players")
    return _style(fig, title)


def bar(df: pd.DataFrame, x: str, y: str, title: str, horizontal: bool = False,
        color: str | None = None, height: int = 380) -> go.Figure:
    """Generic bar chart."""
    if horizontal:
        fig = px.bar(df, x=y, y=x, orientation="h", color=color, text=y,
                     color_discrete_sequence=PALETTE)
        fig.update_yaxes(categoryorder="total ascending", title="")
    else:
        fig = px.bar(df, x=x, y=y, color=color, text=y, color_discrete_sequence=PALETTE)
        fig.update_xaxes(title="")
    fig.update_traces(textposition="outside", cliponaxis=False)
    return _style(fig, title, height)


def donut(df: pd.DataFrame, names: str, values: str, title: str) -> go.Figure:
    """Donut chart."""
    fig = px.pie(df, names=names, values=values, hole=0.55, color_discrete_sequence=PALETTE)
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(showlegend=False)
    return _style(fig, title)


def sunburst(df: pd.DataFrame, path: list[str], title: str) -> go.Figure:
    """Hierarchy chart; each input row counts as one."""
    fig = px.sunburst(df, path=path, color_discrete_sequence=PALETTE)
    fig.update_traces(textinfo="label+value")
    return _style(fig, title, height=460)


def country_bubble(df: pd.DataFrame, title: str = "Depth vs quality by country") -> go.Figure:
    """Competitors (x) vs average points (y); bubble size = total points."""
    fig = px.scatter(df, x="competitors", y="avg_points", size="total_points", color="best_rank",
                     hover_name="country", text="country_code", size_max=45,
                     color_continuous_scale="Greens_r")
    fig.update_traces(textposition="top center")
    fig.update_xaxes(title="Ranked competitors")
    fig.update_yaxes(title="Average points")
    return _style(fig, title, height=440)


def country_treemap(df: pd.DataFrame, title: str = "Share of total ranking points") -> go.Figure:
    """Treemap sized by total points, coloured by average points."""
    fig = px.treemap(df, path=["country"], values="total_points", color="avg_points",
                     color_continuous_scale=GREENS)
    return _style(fig, title, height=440)


def history_chart(df: pd.DataFrame, title: str = "Rank history") -> go.Figure:
    """Rank (inverted axis) and points over stored weekly snapshots."""
    labels = df["ranking_year"].astype(str) + "-W" + df["ranking_week"].astype(str).str.zfill(2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=labels, y=df["rank"], name="Rank", mode="lines+markers",
                             line=dict(color=PALETTE[0])))
    fig.add_trace(go.Scatter(x=labels, y=df["points"], name="Points", mode="lines+markers",
                             line=dict(color=PALETTE[1], dash="dot"), yaxis="y2"))
    fig.update_layout(yaxis=dict(title="Rank", autorange="reversed"),
                      yaxis2=dict(title="Points", overlaying="y", side="right"))
    return _style(fig, title)


def percentile_gauge(value: float, title: str) -> go.Figure:
    """Gauge showing a 0-100 percentile."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value, number=dict(suffix="%"),
        gauge=dict(axis=dict(range=[0, 100]), bar=dict(color=PALETTE[0]),
                   steps=[dict(range=[0, 50], color="#E2E8F0"), dict(range=[50, 100], color="#DCFCE7")]),
    ))
    return _style(fig, title, height=250)

