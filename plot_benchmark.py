import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("benchmark_results.csv")

print(df)

plt.figure(figsize=(10, 6))

plt.bar(
    df["Query"],
    df["Average_ms"]
)

plt.xlabel("Query")
plt.ylabel("Average Execution Time (ms)")
plt.title("Neo4j Query Benchmark Performance")

plt.xticks(rotation=30, ha="right")

plt.tight_layout()

plt.savefig("neo4j_benchmark.png", dpi=300)

plt.show()

print("\nGraph saved as neo4j_benchmark.png")