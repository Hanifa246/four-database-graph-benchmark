import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "results/four_database_speedup.csv"
OUTPUT_FILE = "results/four_database_speedup.png"

df = pd.read_csv(INPUT_FILE)

# Remove CognoDB baseline
df = df[df["Database"] != "CognoDB"].copy()

# Create pivot
pivot = df.pivot_table(
    index="Workload",
    columns="Database",
    values="Speedup_vs_CognoDB"
)

workload_order = [
    "Node_Count_Aggregation",
    "Indexed_Point_Lookup",
    "1-Hop",
    "2-Hop",
    "3-Hop"
]

pivot = pivot.reindex(workload_order)

ax = pivot.plot(
    kind="bar",
    figsize=(14, 8)
)

ax.set_title(
    "Database Speedup Relative to CognoDB",
    fontsize=16
)

ax.set_xlabel("Workload")
ax.set_ylabel("Speedup (×)")

plt.xticks(rotation=20)
plt.legend(title="Database")
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=300
)

plt.close()

print("=" * 70)
print("SPEEDUP GRAPH CREATED")
print("=" * 70)
print(f"Output: {OUTPUT_FILE}")