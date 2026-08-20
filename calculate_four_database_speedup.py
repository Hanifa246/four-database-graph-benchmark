import pandas as pd

INPUT_FILE = "results/four_database_comparison.csv"
OUTPUT_FILE = "results/four_database_speedup.csv"

df = pd.read_csv(INPUT_FILE)

# Keep latency workloads
latency = df[df["Average_ms"].notna()].copy()

# Normalize workload names
latency["Workload"] = (
    latency["Workload"]
    .str.replace("1-hop", "1-Hop", regex=False)
    .str.replace("2-hop", "2-Hop", regex=False)
    .str.replace("3-hop", "3-Hop", regex=False)
)

# Use CognoDB as the baseline
baseline = (
    latency[latency["Database"] == "CognoDB"]
    [["Workload", "Average_ms"]]
    .rename(columns={"Average_ms": "CognoDB_Average_ms"})
)

result = latency.merge(
    baseline,
    on="Workload",
    how="left"
)

# For latency:
# >1 means the database is faster than CognoDB
result["Speedup_vs_CognoDB"] = (
    result["CognoDB_Average_ms"] /
    result["Average_ms"]
)

result = result[
    [
        "Database",
        "Workload",
        "Average_ms",
        "CognoDB_Average_ms",
        "Speedup_vs_CognoDB"
    ]
]

result["Speedup_vs_CognoDB"] = result[
    "Speedup_vs_CognoDB"
].round(2)

result.to_csv(
    OUTPUT_FILE,
    index=False
)

print("=" * 70)
print("FOUR DATABASE SPEEDUP ANALYSIS")
print("=" * 70)
print(result.to_string(index=False))
print()
print(f"Output: {OUTPUT_FILE}")