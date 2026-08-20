import pandas as pd

INPUT_FILE = "results/four_database_comparison.csv"
OUTPUT_FILE = "results/final_four_database_summary.csv"

df = pd.read_csv(INPUT_FILE)

# ---------------------------------------------------------
# LATENCY SUMMARY
# ---------------------------------------------------------

latency = df[df["Average_ms"].notna()].copy()

latency["Workload"] = (
    latency["Workload"]
    .str.replace("1-hop", "1-Hop", regex=False)
    .str.replace("2-hop", "2-Hop", regex=False)
    .str.replace("3-hop", "3-Hop", regex=False)
)

summary_rows = []

for workload in latency["Workload"].unique():

    data = latency[
        latency["Workload"] == workload
    ]

    fastest = data.loc[
        data["Average_ms"].idxmin()
    ]

    slowest = data.loc[
        data["Average_ms"].idxmax()
    ]

    summary_rows.append({
        "Workload": workload,
        "Fastest_Database": fastest["Database"],
        "Fastest_Average_ms": fastest["Average_ms"],
        "Slowest_Database": slowest["Database"],
        "Slowest_Average_ms": slowest["Average_ms"],
        "Performance_Gap_x": round(
            slowest["Average_ms"] /
            fastest["Average_ms"],
            2
        )
    })

summary = pd.DataFrame(summary_rows)

# ---------------------------------------------------------
# MIXED WORKLOAD SUMMARY
# ---------------------------------------------------------

mixed = df[
    df["Operations_per_second"].notna()
].copy()

mixed_rows = []

for concurrency in sorted(
    mixed["Concurrency"].unique()
):

    data = mixed[
        mixed["Concurrency"] == concurrency
    ]

    fastest = data.loc[
        data["Operations_per_second"].idxmax()
    ]

    slowest = data.loc[
        data["Operations_per_second"].idxmin()
    ]

    mixed_rows.append({
        "Concurrency": concurrency,
        "Highest_Throughput_Database":
            fastest["Database"],
        "Highest_Throughput_ops_s":
            fastest["Operations_per_second"],
        "Lowest_Throughput_Database":
            slowest["Database"],
        "Lowest_Throughput_ops_s":
            slowest["Operations_per_second"]
    })

mixed_summary = pd.DataFrame(mixed_rows)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

summary.to_csv(
    OUTPUT_FILE,
    index=False
)

mixed_summary.to_csv(
    "results/final_mixed_workload_summary.csv",
    index=False
)

print("=" * 70)
print("FINAL DATABASE PERFORMANCE SUMMARY")
print("=" * 70)

print("\nLATENCY SUMMARY")
print(summary.to_string(index=False))

print("\nMIXED WORKLOAD SUMMARY")
print(mixed_summary.to_string(index=False))

print("\nFiles created:")
print("results/final_four_database_summary.csv")
print("results/final_mixed_workload_summary.csv")