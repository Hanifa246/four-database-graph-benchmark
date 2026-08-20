import os
import csv
import time
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

USERNAME = os.getenv("MEMGRAPH_USERNAME")
PASSWORD = os.getenv("MEMGRAPH_PASSWORD")
HOST = os.getenv("MEMGRAPH_HOST")
PORT = os.getenv("MEMGRAPH_PORT")

URI = f"bolt+ssc://{HOST}:{PORT}"

CSV_FILE = r"data\processed\pokec_100k_edges.csv"

NODE_BATCH_SIZE = 50000
EDGE_BATCH_SIZE = 50000

print("=" * 60)
print("FAST MEMGRAPH DATA LOADING")
print("=" * 60)

start = time.perf_counter()

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD),
    max_connection_pool_size=10
)

try:
    driver.verify_connectivity()
    print("Memgraph connection: SUCCESS")

    with driver.session() as session:

        # --------------------------------------------------
        # 1. CLEAR EXISTING GRAPH
        # --------------------------------------------------
        print("\nClearing existing graph...")

        session.run(
            "MATCH (n) DETACH DELETE n"
        ).consume()

        print("Graph cleared.")

        # --------------------------------------------------
        # 2. CREATE INDEX
        # --------------------------------------------------
        print("\nCreating index on User.id...")

        try:
            session.run(
                "CREATE INDEX ON :User(id)"
            ).consume()
            print("Index created.")
        except Exception:
            print("Index already exists or was already created.")

        # --------------------------------------------------
        # 3. READ CSV
        # --------------------------------------------------
        print("\nReading CSV...")

        edges = []

        with open(
            CSV_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                edges.append(
                    (
                        int(row["source"]),
                        int(row["target"])
                    )
                )

        print(f"Edges read: {len(edges):,}")

        # --------------------------------------------------
        # 4. GET UNIQUE NODE IDS
        # --------------------------------------------------
        print("\nFinding unique nodes...")

        node_ids = set()

        for source, target in edges:
            node_ids.add(source)
            node_ids.add(target)

        node_ids = list(node_ids)

        print(f"Unique nodes: {len(node_ids):,}")

        # --------------------------------------------------
        # 5. CREATE NODES
        # --------------------------------------------------
        print("\nCreating nodes...")

        for i in range(
            0,
            len(node_ids),
            NODE_BATCH_SIZE
        ):

            batch = node_ids[
                i:i + NODE_BATCH_SIZE
            ]

            session.run(
                """
                UNWIND $ids AS id
                MERGE (:User {id: id})
                """,
                ids=batch
            ).consume()

            loaded = min(
                i + NODE_BATCH_SIZE,
                len(node_ids)
            )

            print(
                f"Nodes: {loaded:,}/{len(node_ids):,}"
            )

        # --------------------------------------------------
        # 6. CREATE RELATIONSHIPS
        # --------------------------------------------------
        print("\nCreating relationships...")

        for i in range(
            0,
            len(edges),
            EDGE_BATCH_SIZE
        ):

            batch_edges = edges[
                i:i + EDGE_BATCH_SIZE
            ]

            rows = [
                {
                    "source": source,
                    "target": target
                }
                for source, target in batch_edges
            ]

            session.run(
                """
                UNWIND $rows AS row

                MATCH (s:User {id: row.source})
                MATCH (t:User {id: row.target})

                CREATE (s)-[:KNOWS]->(t)
                """,
                rows=rows
            ).consume()

            loaded = min(
                i + EDGE_BATCH_SIZE,
                len(edges)
            )

            print(
                f"Relationships: "
                f"{loaded:,}/{len(edges):,}"
            )

        # --------------------------------------------------
        # 7. VERIFY
        # --------------------------------------------------
        print("\nVerifying database...")

        node_count = session.run(
            """
            MATCH (n:User)
            RETURN count(n) AS count
            """
        ).single()["count"]

        relationship_count = session.run(
            """
            MATCH ()-[r:KNOWS]->()
            RETURN count(r) AS count
            """
        ).single()["count"]

        elapsed = time.perf_counter() - start

        # --------------------------------------------------
        # 8. RESULTS
        # --------------------------------------------------
        print("\n" + "=" * 60)
        print("LOAD COMPLETE")
        print("=" * 60)

        print(f"Nodes:         {node_count:,}")
        print(f"Relationships: {relationship_count:,}")
        print(f"Time:          {elapsed:.2f} seconds")

        print("=" * 60)

except Exception as e:

    print("\nLOAD FAILED")
    print(type(e).__name__)
    print(e)

finally:

    driver.close()