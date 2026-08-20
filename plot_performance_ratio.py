import csv
import matplotlib.pyplot as plt

queries = []
memgraph_vs_neo4j = []
cognodb_vs_neo4j = []
cognodb_vs_memgraph = []

with open("three_database_comparison.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        queries.append(row["Query"])
        memgraph_vs_neo4j.append(float(row["Memgraph_vs_Neo4j"]))
        cognodb_vs_neo4j.append(float(row["CognoDB_vs_Neo4j"]))
        cognodb_vs_memgraph.append(float(row["CognoDB_vs_Memgraph"]))

x = range(len(queries))

plt.figure(figsize=(12, 6))

width = 0.25

plt.bar(
    [i - width for i in x],
    memgraph_vs_neo4j,
    width=width,
    label="Memgraph vs Neo4j"
)

plt.bar(
    x,
    cognodb_vs_neo4j,
    width=width,
    label="CognoDB vs Neo4j"
)

plt.bar(
    [i + width for i in x],
    cognodb_vs_memgraph,
    width=width,
    label="CognoDB vs Memgraph"
)

plt.xlabel("Query")
plt.ylabel("Performance Ratio (×)")
plt.title("Three-Database Performance Ratio Comparison")

plt.xticks(list(x), queries, rotation=30, ha="right")

plt.legend()
plt.tight_layout()

plt.savefig(
    "performance_ratio_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("Graph saved as performance_ratio_comparison.png")