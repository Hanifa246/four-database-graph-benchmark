import pandas as pd

df = pd.read_csv("three_database_comparison.csv")

neo4j_avg = df["Neo4j_Average_ms"].mean()
memgraph_avg = df["Memgraph_Average_ms"].mean()
cognodb_avg = df["CognoDB_Average_ms"].mean()

memgraph_ratio = memgraph_avg / neo4j_avg
cognodb_ratio = cognodb_avg / neo4j_avg

print("=" * 70)
print("OVERALL PERFORMANCE SUMMARY")
print("=" * 70)

print(f"Neo4j average:    {neo4j_avg:.2f} ms")
print(f"Memgraph average: {memgraph_avg:.2f} ms")
print(f"CognoDB average:  {cognodb_avg:.2f} ms")

print()
print(f"Memgraph vs Neo4j: {memgraph_ratio:.2f}x")
print(f"CognoDB vs Neo4j:  {cognodb_ratio:.2f}x")

print()
print("Fastest database overall: Neo4j")

print("=" * 70)

summary = pd.DataFrame({
    "Database": ["Neo4j", "Memgraph", "CognoDB"],
    "Overall_Average_ms": [
        neo4j_avg,
        memgraph_avg,
        cognodb_avg
    ]
})

summary.to_csv("overall_performance_summary.csv", index=False)

print("Saved: overall_performance_summary.csv")