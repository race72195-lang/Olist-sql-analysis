"""
Runs every SQL file in queries/, saves the result tables to results/,
draws charts to images/ and prints a short list of findings for the README.

Usage:  python run_analysis.py
"""

import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # save charts to files, do not open windows
import matplotlib.pyplot as plt
import pandas as pd

from load_data import DB_PATH, build_db

BASE_DIR = Path(__file__).resolve().parent
QUERIES_DIR = BASE_DIR / "queries"
RESULTS_DIR = BASE_DIR / "results"
IMAGES_DIR = BASE_DIR / "images"
RESULTS_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)


SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
BLUE, ORANGE = "#2a78d6", "#eb6834"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "font.size": 11,
})


def style(ax, grid_axis="y"):
    """Quiet axes: no top/right frame, light grid."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def money(v):
    return f"R${v / 1e6:.2f}M" if v >= 1e6 else f"R${v / 1e3:,.0f}k"


def save(fig, name):
    fig.tight_layout()
    fig.savefig(IMAGES_DIR / name, dpi=150)
    plt.close(fig)
    print(f"  saved images/{name}")



def run_queries(conn):
    tables = {}
    for sql_file in sorted(QUERIES_DIR.glob("*.sql")):
        sql = sql_file.read_text(encoding="utf-8")
        title = sql.splitlines()[0].lstrip("- ").strip()
        df = pd.read_sql_query(sql, conn)
        df.to_csv(RESULTS_DIR / f"{sql_file.stem}.csv", index=False)
        tables[sql_file.stem] = df
        print(f"\n=== {sql_file.stem}: {title}")
        print(df.head(10).to_string(index=False))
    return tables


def chart_monthly(df):
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(df["month"], df["revenue"], color=BLUE, linewidth=2, marker="o", markersize=4)
    ax.plot(df["month"], df["revenue_3m_avg"], color=INK2, linewidth=1.5, linestyle="--")
    ax.set_xticks(range(0, len(df), 2))
    ax.set_xticklabels(df["month"].iloc[::2], rotation=45, ha="right")
    ax.yaxis.set_major_formatter(lambda v, _: money(v))
    last = df.iloc[-1]
    ax.annotate(money(last["revenue"]), (len(df) - 1, last["revenue"]),
                textcoords="offset points", xytext=(-4, 8), ha="right", color=INK)
    ax.text(0.01, 0.97, "solid = monthly revenue   dashed = 3-month average",
            transform=ax.transAxes, color=INK2, va="top", fontsize=9.5)
    ax.set_title(f"Monthly revenue of delivered orders, {df['month'].iloc[0]} to {df['month'].iloc[-1]}",
                 loc="left", fontweight="bold")
    style(ax)
    save(fig, "01_monthly_revenue.png")


def chart_categories(df):
    top = df.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.barh(top["category"], top["revenue"], color=BLUE, height=0.65)
    for y, (rev, share) in enumerate(zip(top["revenue"], top["revenue_share_pct"])):
        ax.text(rev, y, f"  {money(rev)}  ({share}%)", va="center", color=INK, fontsize=10)
    ax.set_xlim(0, top["revenue"].max() * 1.25)
    ax.xaxis.set_major_formatter(lambda v, _: money(v))
    ax.set_title("Top 10 product categories by revenue", loc="left", fontweight="bold")
    style(ax, grid_axis="x")
    save(fig, "02_top_categories.png")


def chart_delivery_state(df):
    d = df.sort_values("avg_delivery_days").tail(12)
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.barh(d["state"], d["avg_delivery_days"], color=BLUE, height=0.65)
    for y, (days, late) in enumerate(zip(d["avg_delivery_days"], d["late_pct"])):
        ax.text(days, y, f"  {days} days, {late}% late", va="center", color=INK, fontsize=10)
    ax.set_xlim(0, d["avg_delivery_days"].max() * 1.3)
    ax.set_title("Average delivery time by customer state (days from purchase)",
                 loc="left", fontweight="bold")
    style(ax, grid_axis="x")
    save(fig, "03_delivery_by_state.png")


def chart_reviews(df):
    labels = [b.split(". ", 1)[1].replace(" (up to 7 days early)", "").replace(" days", "\ndays", 1)
              for b in df["delivery_bucket"]]
    colors = [BLUE if i < 2 else ORANGE for i in range(len(df))]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    bars = ax.bar(labels, df["avg_review_score"], color=colors, width=0.6)
    for bar, score, n in zip(bars, df["avg_review_score"], df["orders"]):
        ax.text(bar.get_x() + bar.get_width() / 2, score + 0.08, f"{score:.2f}",
                ha="center", color=INK, fontweight="bold")
        ax.text(bar.get_x() + bar.get_width() / 2, 0.12, f"{n:,} orders",
                ha="center", color="white", fontsize=9)
    ax.set_ylim(0, 5)
    ax.set_ylabel("Average review score (1-5)")
    ax.set_title("Average review score by delivery timing (vs estimated date)", loc="left", fontweight="bold")
    style(ax)
    save(fig, "04_reviews_vs_delivery.png")


def chart_sellers(df):
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    ax.plot([0, 100], [0, 100], color=GRID, linestyle="--", linewidth=1.5)
    ax.plot(df["pct_of_sellers"], df["cumulative_revenue_pct"], color=BLUE, linewidth=2.5)
    top10 = df[df["pct_of_sellers"] <= 10]["cumulative_revenue_pct"].max()
    ax.scatter([10], [top10], color=ORANGE, zorder=3)
    ax.annotate(f"Top 10% of sellers\n= {top10:.0f}% of revenue", (10, top10),
                textcoords="offset points", xytext=(14, -26), color=INK)
    ax.text(62, 52, "equal share", color=INK2, rotation=33, fontsize=9.5)
    ax.set_xlabel("Share of sellers, %  (biggest first)")
    ax.set_ylabel("Share of revenue, %")
    ax.set_xlim(0, 100); ax.set_ylim(0, 100)
    ax.set_title("Share of revenue vs share of sellers", loc="left", fontweight="bold")
    style(ax)
    save(fig, "05_seller_concentration.png")


def findings(t):
    lines = []
    m = t["02_monthly_revenue"]
    lines.append(f"Revenue grew from {money(m['revenue'].iloc[0])} in {m['month'].iloc[0]} "
                 f"to {money(m['revenue'].iloc[-1])} in {m['month'].iloc[-1]}.")
    c = t["03_top_categories"]
    lines.append(f"'{c['category'].iloc[0]}' is the #1 category ({c['revenue_share_pct'].iloc[0]}% of revenue); "
                 f"the top 3 categories bring {c['cumulative_share_pct'].iloc[2]}%.")
    d = t["06_reviews_vs_delivery"]
    good = d.iloc[1]["avg_review_score"]
    worst = d.iloc[-1]["avg_review_score"]
    lines.append(f"Average review score is {good} for on-time orders and {worst} for orders "
                 f"more than 7 days late ({d.iloc[-1]['bad_review_pct']}% of them get 1-2 stars).")
    s = t["05_delivery_by_state"]
    lines.append(f"Slowest state: {s.iloc[0]['state']} ({s.iloc[0]['avg_delivery_days']} days); "
                 f"fastest: {s.iloc[-1]['state']} ({s.iloc[-1]['avg_delivery_days']} days).")
    r = t["07_repeat_customers"]
    one = r.loc[r["segment"] == "1 order", "customers_pct"].iloc[0]
    lines.append(f"{one}% of customers bought only once; {round(100 - one, 1)}% came back.")
    k = t["09_seller_concentration"]
    top10 = k[k["pct_of_sellers"] <= 10]["cumulative_revenue_pct"].max()
    lines.append(f"The top 10% of sellers generate {top10:.0f}% of revenue.")
    p = t["08_payment_methods"]
    lines.append(f"'{p['payment_type'].iloc[0]}' is the main payment method "
                 f"({p['value_share_pct'].iloc[0]}% of payment value).")
    text = "\n".join(f"- {x}" for x in lines)
    (RESULTS_DIR / "findings.txt").write_text(text, encoding="utf-8")
    print("\n" + "=" * 70 + "\nKEY FINDINGS (copy into README)\n" + "=" * 70)
    print(text)


def main():
    build_db()
    with sqlite3.connect(DB_PATH) as conn:
        tables = run_queries(conn)
    print("\nDrawing charts...")
    chart_monthly(tables["02_monthly_revenue"])
    chart_categories(tables["03_top_categories"])
    chart_delivery_state(tables["05_delivery_by_state"])
    chart_reviews(tables["06_reviews_vs_delivery"])
    chart_sellers(tables["09_seller_concentration"])
    findings(tables)
    print("\nDone. Tables are in results/, charts are in images/.")


if __name__ == "__main__":
    main()
