import pandas as pd

df = pd.read_csv("three_database_comparison.csv")

result = df[
    [
        "Query",
        "Neo4j_Average_ms",
        "Memgraph_Average_ms",
        "CognoDB_Average_ms"
    ]
].copy()

result["Fastest_Database"] = result[
    [
        "Neo4j_Average_ms",
        "Memgraph_Average_ms",
        "CognoDB_Average_ms"
    ]
].idxmin(axis=1)

result["Fastest_Database"] = result["Fastest_Database"].replace({
    "Neo4j_Average_ms": "Neo4j",
    "Memgraph_Average_ms": "Memgraph",
    "CognoDB_Average_ms": "CognoDB"
})

result.to_csv("final_benchmark_results.csv", index=False)

print("=" * 70)
print("FINAL THREE-DATABASE BENCHMARK RESULTS")
print("=" * 70)
print(result.to_string(index=False))
print("=" * 70)
print("Results saved as final_benchmark_results.csv")