import pandas as pd

# ---------------------------------------------------------
# FILES
# ---------------------------------------------------------

NEO4J_FILE = "advanced_benchmark_results.csv"

MEMGRAPH_FILE = "memgraph_benchmark_results.csv"

COGNODB_FILE = "advanced_benchmark_cognodb_results.csv"

OUTPUT_FILE = "three_database_comparison.csv"

# ---------------------------------------------------------
# LOAD RESULTS
# ---------------------------------------------------------

neo4j = pd.read_csv(NEO4J_FILE)
memgraph = pd.read_csv(MEMGRAPH_FILE)
cognodb = pd.read_csv(COGNODB_FILE)

# ---------------------------------------------------------
# SELECT REQUIRED COLUMNS
# ---------------------------------------------------------

neo4j = neo4j[["Query", "Average_ms"]]
memgraph = memgraph[["Query", "Average_ms"]]
cognodb = cognodb[["Query", "Average_ms"]]

# ---------------------------------------------------------
# RENAME COLUMNS
# ---------------------------------------------------------

neo4j = neo4j.rename(
    columns={"Average_ms": "Neo4j_Average_ms"}
)

memgraph = memgraph.rename(
    columns={"Average_ms": "Memgraph_Average_ms"}
)

cognodb = cognodb.rename(
    columns={"Average_ms": "CognoDB_Average_ms"}
)

# ---------------------------------------------------------
# MERGE
# ---------------------------------------------------------

comparison = neo4j.merge(
    memgraph,
    on="Query"
).merge(
    cognodb,
    on="Query"
)

# ---------------------------------------------------------
# CALCULATE SPEEDUPS
# ---------------------------------------------------------

comparison["Memgraph_vs_Neo4j"] = (
    comparison["Memgraph_Average_ms"]
    / comparison["Neo4j_Average_ms"]
)

comparison["CognoDB_vs_Neo4j"] = (
    comparison["CognoDB_Average_ms"]
    / comparison["Neo4j_Average_ms"]
)

comparison["CognoDB_vs_Memgraph"] = (
    comparison["CognoDB_Average_ms"]
    / comparison["Memgraph_Average_ms"]
)

# ---------------------------------------------------------
# ROUND VALUES
# ---------------------------------------------------------

comparison[
    [
        "Neo4j_Average_ms",
        "Memgraph_Average_ms",
        "CognoDB_Average_ms",
        "Memgraph_vs_Neo4j",
        "CognoDB_vs_Neo4j",
        "CognoDB_vs_Memgraph"
    ]
] = comparison[
    [
        "Neo4j_Average_ms",
        "Memgraph_Average_ms",
        "CognoDB_Average_ms",
        "Memgraph_vs_Neo4j",
        "CognoDB_vs_Neo4j",
        "CognoDB_vs_Memgraph"
    ]
].round(2)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

comparison.to_csv(
    OUTPUT_FILE,
    index=False
)

# ---------------------------------------------------------
# DISPLAY
# ---------------------------------------------------------

print("=" * 80)
print("NEO4J VS COGNODB VS MEMGRAPH")
print("=" * 80)

for _, row in comparison.iterrows():

    print(
        f"{row['Query']:<20}"
        f"Neo4j: {row['Neo4j_Average_ms']:>8.2f} ms   "
        f"Memgraph: {row['Memgraph_Average_ms']:>8.2f} ms   "
        f"CognoDB: {row['CognoDB_Average_ms']:>8.2f} ms"
    )

print("\n" + "=" * 80)
print("COMPARISON SAVED TO:")
print(OUTPUT_FILE)
print("=" * 80)