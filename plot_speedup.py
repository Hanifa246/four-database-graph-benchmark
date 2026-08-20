import csv
import matplotlib.pyplot as plt

input_file = "three_database_comparison.csv"

queries = []
memgraph_vs_neo4j = []
cognodb_vs_neo4j = []
cognodb_vs_memgraph = []

with open(input_file, "r", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)

    for row in reader:
        queries.append(row["Query"])
        memgraph_vs_neo4j.append(float(row["Memgraph_vs_Neo4j"]))
        cognodb_vs_neo4j.append(float(row["CognoDB_vs_Neo4j"]))
        cognodb_vs_memgraph.append(float(row["CognoDB_vs_Memgraph"]))

x = range(len(queries))
width = 0.25

plt.figure(figsize=(12, 6))

plt.bar(
    [i - width for i in x],
    memgraph_vs_neo4j,
    width=width,
    label="Memgraph / Neo4j"
)

plt.bar(
    x,
    cognodb_vs_neo4j,
    width=width,
    label="CognoDB / Neo4j"
)

plt.bar(
    [i + width for i in x],
    cognodb_vs_memgraph,
    width=width,
    label="CognoDB / Memgraph"
)

plt.xlabel("Query")
plt.ylabel("Performance Ratio (×)")
plt.title("Performance Ratio: Neo4j vs Memgraph vs CognoDB")

plt.xticks(list(x), queries, rotation=30)
plt.legend()
plt.tight_layout()

plt.savefig("performance_ratio_comparison.png", dpi=300)

plt.show()

print("Graph saved successfully as:")
print("performance_ratio_comparison.png")