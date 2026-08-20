import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "results/four_database_comparison.csv"
OUTPUT_FILE = "results/four_database_mixed_workload.png"

df = pd.read_csv(INPUT_FILE)

# Keep only mixed workload rows
mixed = df[
    df["Operations_per_second"].notna()
].copy()

# Plot
plt.figure(figsize=(12, 7))

for database in mixed["Database"].unique():
    data = mixed[mixed["Database"] == database]

    plt.plot(
        data["Concurrency"],
        data["Operations_per_second"],
        marker="o",
        label=database
    )

plt.title(
    "Four-Database Mixed Workload Throughput",
    fontsize=16
)

plt.xlabel("Concurrency")
plt.ylabel("Operations per Second")

plt.xticks([1, 10, 40])
plt.grid(True, alpha=0.3)
plt.legend(title="Database")

plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=300
)

plt.close()

print("=" * 70)
print("MIXED WORKLOAD GRAPH CREATED")
print("=" * 70)
print(f"Output: {OUTPUT_FILE}")