import csv
import matplotlib.pyplot as plt

queries = []
neo4j = []
memgraph = []
cognodb = []

with open(
    "three_database_comparison.csv",
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:
        queries.append(row["Query"])
        neo4j.append(float(row["Neo4j_Average_ms"]))
        memgraph.append(float(row["Memgraph_Average_ms"]))
        cognodb.append(float(row["CognoDB_Average_ms"]))

x = range(len(queries))
width = 0.25

plt.figure(figsize=(14, 7))

plt.bar(
    [i - width for i in x],
    neo4j,
    width,
    label="Neo4j"
)

plt.bar(
    x,
    memgraph,
    width,
    label="Memgraph"
)

plt.bar(
    [i + width for i in x],
    cognodb,
    width,
    label="CognoDB"
)

plt.xlabel("Query")
plt.ylabel("Average Latency (ms)")
plt.title("Neo4j vs Memgraph vs CognoDB")

plt.xticks(
    list(x),
    queries,
    rotation=20
)

# Logarithmic scale
plt.yscale("log")

plt.legend()
plt.tight_layout()

plt.savefig(
    "three_database_comparison_log.png",
    dpi=200,
    bbox_inches="tight"
)

plt.show()

print("Graph saved as: three_database_comparison_log.png")