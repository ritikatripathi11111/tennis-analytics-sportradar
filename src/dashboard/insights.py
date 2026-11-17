"""Rule-based analytics that turn a ranking snapshot into plain-English insights.

Pure pandas/numpy so it can be unit-tested without Streamlit or a database.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _strength(r: float) -> str:
    size = abs(r)
    label = "very weak" if size < .2 else "weak" if size < .4 else "moderate" if size < .6 else "strong"
    return f"{label} {'positive' if r >= 0 else 'negative'}"


def generate_insights(df: pd.DataFrame, tour: str = "") -> list[tuple[str, str]]:
    """Return ``[(headline, explanation), ...]`` for one ranking snapshot."""
    if df.empty:
        return []
    out: list[tuple[str, str]] = []
    label = f"{tour} " if tour else ""

    # 1. Leaders / ties
    top_points = df["points"].max()
    leaders = df[df["points"] == top_points].sort_values("name")
    names = " & ".join(leaders["name"].head(3))
    tie = f" ({len(leaders)} players tied - typical for doubles partners)" if len(leaders) > 1 else ""
    out.append(("Who leads?", f"{names} top the {label}table with {top_points:,} points{tie}."))

    # 2. Country dominance in the top 50
    top50 = df[df["rank"] <= 50]
    if not top50.empty:
        by_country = top50.groupby("country")["points"].agg(["count", "sum"]).sort_values("sum", ascending=False)
        country, row = by_country.index[0], by_country.iloc[0]
        share = 100 * row["sum"] / top50["points"].sum()
        out.append(("Country dominance",
                    f"{country} holds {int(row['count'])} of the top-50 spots and {share:.1f}% of top-50 points."))

    # 3. Concentration of the field
    counts = df["country"].value_counts()
    top3 = counts.head(3)
    out.append(("Field concentration",
                f"The three biggest nations ({', '.join(top3.index)}) account for "
                f"{100 * top3.sum() / len(df):.0f}% of ranked players across {counts.size} countries."))

    # 4. Movers
    up, down = df.loc[df["movement"].idxmax()], df.loc[df["movement"].idxmin()]
    if up["movement"] > 0:
        out.append(("Biggest climber",
                    f"{up['name']} ({up['country']}) moved {int(up['movement'])} places to rank {int(up['rank'])}."))
    if down["movement"] < 0:
        out.append(("Biggest drop",
                    f"{down['name']} ({down['country']}) fell {abs(int(down['movement']))} places to rank {int(down['rank'])}."))
    stable = 100 * (df["movement"] == 0).mean()
    out.append(("Ranking stability", f"{stable:.0f}% of ranked players kept the same position this week."))

    # 5. Efficiency
    active = df[df["competitions_played"] >= 10].copy()
    if not active.empty:
        active["ppe"] = active["points"] / active["competitions_played"]
        best = active.loc[active["ppe"].idxmax()]
        out.append(("Most efficient",
                    f"{best['name']} earns {best['ppe']:.0f} points per event "
                    f"(field median {active['ppe'].median():.0f}, min. 10 events)."))

    # 6. Workload vs success
    if df["competitions_played"].nunique() > 1 and df["points"].nunique() > 1:
        r = float(np.corrcoef(df["competitions_played"], df["points"])[0, 1])
        out.append(("Does playing more pay off?",
                    f"Events played vs points shows a {_strength(r)} relationship (r = {r:.2f})."))
    return out
