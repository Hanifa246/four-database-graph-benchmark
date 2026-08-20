import csv
import time
from pathlib import Path

from connectors.falkordb import create_falkordb_connector


DATA_FILE = Path("data/processed/pokec_100k_edges.csv")

NODE_BATCH_SIZE = 10000
EDGE_BATCH_SIZE = 1000


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
    print("FALKORDB DATASET LOAD")
    print("=" * 70)

    edges = read_edges()

    print(f"Dataset:       {DATA_FILE}")
    print(f"Relationships: {len(edges):,}")
    print()

    connector = create_falkordb_connector()

    try:

        print("Connected to FalkorDB.")

        # Clear old data
        print("Clearing previous benchmark data...")

        connector.run_query("""
            MATCH (n)
            DETACH DELETE n
        """)

        # --------------------------------------------------
        # UNIQUE NODES
        # --------------------------------------------------

        node_ids = set()

        for edge in edges:
            node_ids.add(edge["source"])
            node_ids.add(edge["target"])

        node_ids = list(node_ids)

        print(
            f"Unique nodes: {len(node_ids):,}"
        )

        # --------------------------------------------------
        # CREATE NODES
        # --------------------------------------------------

        print()
        print("Creating nodes...")

        start = time.perf_counter()

        for i in range(
            0,
            len(node_ids),
            NODE_BATCH_SIZE
        ):

            batch = node_ids[
                i:i + NODE_BATCH_SIZE
            ]

            connector.run_query(
                """
                UNWIND $ids AS id
                CREATE (:Node {id: id})
                """,
                {
                    "ids": batch
                }
            )

            loaded = min(
                i + NODE_BATCH_SIZE,
                len(node_ids)
            )

            print(
                f"Nodes: "
                f"{loaded:,}/{len(node_ids):,}"
            )

        node_time = (
            time.perf_counter() - start
        )

        print(
            f"Node loading completed in "
            f"{node_time:.4f} seconds"
        )

        # --------------------------------------------------
        # INDEX
        # --------------------------------------------------

        print()
        print("Creating Node.id index...")

        try:

            connector.run_query(
                """
                CREATE INDEX FOR (n:Node) ON (n.id)
                """
            )

            print("Index created.")

        except Exception as error:

            print(
                "Index note:",
                error
            )

        # --------------------------------------------------
        # RELATIONSHIPS
        # --------------------------------------------------

        print()
        print("Creating relationships...")
        print(
            f"Edge batch size: {EDGE_BATCH_SIZE}"
        )

        relationship_start = (
            time.perf_counter()
        )

        for i in range(
            0,
            len(edges),
            EDGE_BATCH_SIZE
        ):

            batch = edges[
                i:i + EDGE_BATCH_SIZE
            ]

            connector.run_query(
                """
                UNWIND $rows AS row

                MATCH (source:Node)
                WHERE source.id = row.source

                MATCH (target:Node)
                WHERE target.id = row.target

                CREATE (source)-[:CONNECTED_TO]->(target)
                """,
                {
                    "rows": batch
                }
            )

            loaded = min(
                i + EDGE_BATCH_SIZE,
                len(edges)
            )

            print(
                f"Relationships: "
                f"{loaded:,}/{len(edges):,}"
            )

        relationship_time = (
            time.perf_counter()
            - relationship_start
        )

        total_time = (
            node_time +
            relationship_time
        )

        # --------------------------------------------------
        # VERIFY
        # --------------------------------------------------

        print()
        print("Verifying dataset...")

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

        node_count = node_result[0][0]

        relationship_count = (
            relationship_result[0][0]
        )

        print()
        print("=" * 70)
        print("FALKORDB LOAD COMPLETE")
        print("=" * 70)

        print(
            f"Nodes:                 "
            f"{node_count:,}"
        )

        print(
            f"Relationships:         "
            f"{relationship_count:,}"
        )

        print(
            f"Node loading time:     "
            f"{node_time:.4f} seconds"
        )

        print(
            f"Relationship time:     "
            f"{relationship_time:.4f} seconds"
        )

        print(
            f"Total load time:       "
            f"{total_time:.4f} seconds"
        )

        print(
            f"Nodes/second:          "
            f"{node_count / total_time:,.2f}"
        )

        print(
            f"Relationships/second:  "
            f"{relationship_count / total_time:,.2f}"
        )

        print("=" * 70)

    finally:

        connector.close()


if __name__ == "__main__":
    main()