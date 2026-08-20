import csv
import time
from pathlib import Path

from connectors.neo4j_connector import (
    create_cognodb_connector,
    create_aura_connector
)


DATA_FILE = Path("data/processed/pokec_100k_edges.csv")

BATCH_SIZE = 1000


def read_edges():
    edges = []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            edges.append(
                (
                    int(row["source"]),
                    int(row["target"])
                )
            )

    return edges


def load_database(name, connector, edges):

    print("=" * 70)
    print(f"LOADING {name}")
    print("=" * 70)

    connector.verify()

    # Clean previous benchmark data
    print("Clearing previous benchmark data...")

    connector.run_query(
        """
        MATCH (n:Node)
        DETACH DELETE n
        """
    )

    # Create uniqueness constraint/index
    try:
        connector.run_query(
            """
            CREATE CONSTRAINT benchmark_node_id IF NOT EXISTS
            FOR (n:Node)
            REQUIRE n.id IS UNIQUE
            """
        )
    except Exception as error:
        print("Constraint creation note:", error)

    print(f"Loading {len(edges):,} relationships...")
    print(f"Batch size: {BATCH_SIZE}")

    start_time = time.perf_counter()

    total_edges = 0

    for i in range(0, len(edges), BATCH_SIZE):

        batch = edges[i:i + BATCH_SIZE]

        connector.run_query(
            """
            UNWIND $rows AS row

            MERGE (source:Node {id: row.source})
            MERGE (target:Node {id: row.target})

            MERGE (source)-[:CONNECTED_TO]->(target)
            """,
            {
                "rows": [
                    {
                        "source": source,
                        "target": target
                    }
                    for source, target in batch
                ]
            }
        )

        total_edges += len(batch)

        if total_edges % 10000 == 0:
            print(
                f"Loaded {total_edges:,}/"
                f"{len(edges):,} relationships"
            )

    end_time = time.perf_counter()

    elapsed = end_time - start_time

    # Verify counts
    node_result = connector.run_query(
        """
        MATCH (n:Node)
        RETURN count(n) AS count
        """
    )

    relationship_result = connector.run_query(
        """
        MATCH ()-[r:CONNECTED_TO]->()
        RETURN count(r) AS count
        """
    )

    node_count = node_result[0]["count"]
    relationship_count = relationship_result[0]["count"]

    nodes_per_second = (
        node_count / elapsed
        if elapsed > 0
        else 0
    )

    relationships_per_second = (
        relationship_count / elapsed
        if elapsed > 0
        else 0
    )

    print()
    print(f"Nodes:              {node_count:,}")
    print(f"Relationships:      {relationship_count:,}")
    print(f"Load time:          {elapsed:.4f} seconds")
    print(f"Nodes/second:       {nodes_per_second:,.2f}")
    print(
        f"Relationships/sec:  "
        f"{relationships_per_second:,.2f}"
    )

    return {
        "Database": name,
        "Nodes": node_count,
        "Relationships": relationship_count,
        "Load_Time_s": round(elapsed, 4),
        "Nodes_per_second": round(
            nodes_per_second,
            2
        ),
        "Relationships_per_second": round(
            relationships_per_second,
            2
        )
    }


def main():

    print("=" * 70)
    print("WEXA GRAPH DATABASE INGEST BENCHMARK")
    print("=" * 70)

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    edges = read_edges()

    print(
        f"Dataset: {DATA_FILE}"
    )

    print(
        f"Relationships in CSV: {len(edges):,}"
    )

    databases = {
        "CognoDB": create_cognodb_connector(),
        "Neo4j_Aura": create_aura_connector()
    }

    results = []

    try:

        for name, connector in databases.items():

            result = load_database(
                name,
                connector,
                edges
            )

            results.append(result)

    finally:

        for connector in databases.values():
            connector.close()

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    output_file = (
        output_dir /
        "load_results.csv"
    )

    fieldnames = [
        "Database",
        "Nodes",
        "Relationships",
        "Load_Time_s",
        "Nodes_per_second",
        "Relationships_per_second"
    ]

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)

    print()
    print("=" * 70)
    print("LOAD BENCHMARK COMPLETE")
    print(f"Results saved to: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()