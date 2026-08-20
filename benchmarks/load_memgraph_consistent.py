import csv
import time
from pathlib import Path

from connectors.memgraph_connector import create_memgraph_connector


DATA_FILE = Path("data/processed/pokec_100k_edges.csv")
BATCH_SIZE = 1000


def read_edges():
    edges = []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            edges.append({
                "source": int(row["source"]),
                "target": int(row["target"])
            })

    return edges


def main():

    print("=" * 70)
    print("MEMGRAPH CONSISTENT DATASET LOAD")
    print("=" * 70)

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    edges = read_edges()

    print(f"Dataset: {DATA_FILE}")
    print(f"Relationships: {len(edges):,}")
    print(f"Batch size: {BATCH_SIZE}")

    connector = create_memgraph_connector()

    try:

        connector.verify()

        print("\nConnected to Memgraph.")

        print("\nClearing previous benchmark data...")

        connector.run_query(
            """
            MATCH (n)
            DETACH DELETE n
            """
        )

        print("Creating index...")

        try:
            connector.run_query(
                """
                CREATE INDEX ON :Node(id)
                """
            )
        except Exception as error:
            print(
                "Index creation note:",
                error
            )

        print("\nLoading dataset...")

        start_time = time.perf_counter()

        for i in range(
            0,
            len(edges),
            BATCH_SIZE
        ):

            batch = edges[
                i:i + BATCH_SIZE
            ]

            connector.run_query(
                """
                UNWIND $rows AS row

                MERGE (source:Node {
                    id: row.source
                })

                MERGE (target:Node {
                    id: row.target
                })

                MERGE (
                    source
                )-[:CONNECTED_TO]->(
                    target
                )
                """,
                {
                    "rows": batch
                }
            )

            loaded = min(
                i + BATCH_SIZE,
                len(edges)
            )

            if loaded % 10000 == 0:
                print(
                    f"Loaded {loaded:,}/"
                    f"{len(edges):,}"
                )

        elapsed = (
            time.perf_counter()
            - start_time
        )

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
        relationship_count = (
            relationship_result[0]["count"]
        )

        nodes_per_second = (
            node_count / elapsed
        )

        relationships_per_second = (
            relationship_count / elapsed
        )

        print("\n" + "=" * 70)
        print("MEMGRAPH LOAD COMPLETE")
        print("=" * 70)

        print(
            f"Nodes:                 {node_count:,}"
        )

        print(
            f"Relationships:         "
            f"{relationship_count:,}"
        )

        print(
            f"Load time:             "
            f"{elapsed:.4f} seconds"
        )

        print(
            f"Nodes/second:          "
            f"{nodes_per_second:,.2f}"
        )

        print(
            f"Relationships/second:  "
            f"{relationships_per_second:,.2f}"
        )

        print("=" * 70)

    finally:

        connector.close()


if __name__ == "__main__":
    main()