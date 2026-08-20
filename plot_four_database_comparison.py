import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "results/four_database_comparison.csv"
OUTPUT_FILE = "results/four_database_performance.png"

df = pd.read_csv(INPUT_FILE)

# Keep latency workloads only
latency = df[df["Average_ms"].notna()].copy()

# Normalize workload names
latency["Workload"] = latency["Workload"].str.replace(
    "1-Hop", "1-Hop"
).str.replace(
    "2-Hop", "2-Hop"
).str.replace(
    "3-Hop", "3-Hop"
).str.replace(
    "1-hop", "1-Hop"
).str.replace(
    "2-hop", "2-Hop"
).str.replace(
    "3-hop", "3-Hop"
)

# Pivot
pivot = latency.pivot_table(
    index="Workload",
    columns="Database",
    values="Average_ms"
)

# Desired order
workload_order = [
    "Node_Count_Aggregation",
    "Indexed_Point_Lookup",
    "1-Hop",
    "2-Hop",
    "3-Hop"
]

pivot = pivot.reindex(workload_order)

# Plot
ax = pivot.plot(
    kind="bar",
    figsize=(14, 8)
)

ax.set_title(
    "Four-Database Performance Comparison",
    fontsize=16
)

ax.set_xlabel("Workload")
ax.set_ylabel("Average Latency (ms)")

plt.xticks(rotation=20)
plt.legend(title="Database")
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=300)

print("=" * 70)
print("FOUR DATABASE PERFORMANCE GRAPH CREATED")
print("=" * 70)
print(f"Output: {OUTPUT_FILE}")