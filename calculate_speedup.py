import csv

input_file = "three_database_comparison.csv"

print("=" * 80)
print("PERFORMANCE RATIO ANALYSIS")
print("=" * 80)

print(
    f"{'Query':<25}"
    f"{'Memgraph/Neo4j':>18}"
    f"{'CognoDB/Neo4j':>20}"
    f"{'CognoDB/Memgraph':>22}"
)

print("-" * 80)

with open(input_file, "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        query = row["Query"]

        neo4j = float(row["Neo4j_Average_ms"])
        memgraph = float(row["Memgraph_Average_ms"])
        cognodb = float(row["CognoDB_Average_ms"])

        memgraph_vs_neo4j = memgraph / neo4j
        cognodb_vs_neo4j = cognodb / neo4j
        cognodb_vs_memgraph = cognodb / memgraph

        print(
            f"{query:<25}"
            f"{memgraph_vs_neo4j:>18.2f}x"
            f"{cognodb_vs_neo4j:>20.2f}x"
            f"{cognodb_vs_memgraph:>22.2f}x"
        )

print("-" * 80)
print("Analysis completed successfully.")