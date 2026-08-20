import os
import csv
import time
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

CSV_FILE = Path("data/processed/pokec_100k_edges.csv")

BATCH_SIZE = 5000


# ============================================================
# VALIDATION
# ============================================================

if not URI:
    raise ValueError("COGNODB_URI is missing")

if not USERNAME:
    raise ValueError("COGNODB_USERNAME is missing")

if not PASSWORD:
    raise ValueError("COGNODB_PASSWORD is missing")

if not CSV_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found: {CSV_FILE.resolve()}"
    )


# ============================================================
# CONNECT
# ============================================================

print("=" * 60)
print("             COGNODB DATA LOADER")
print("=" * 60)

print()
print("Dataset:")
print(CSV_FILE.resolve())

print()
print("Connecting to CognoDB...")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

driver.verify_connectivity()

print("✅ Connected to CognoDB")


# ============================================================
# CREATE CONSTRAINT
# ============================================================

print()
print("Creating node constraint...")

with driver.session() as session:

    session.run("""
        CREATE CONSTRAINT person_id_unique IF NOT EXISTS
        FOR (n:Person)
        REQUIRE n.id IS UNIQUE
    """).consume()

print("✅ Constraint ready")


# ============================================================
# LOAD ONE BATCH
# ============================================================

def load_batch(session, batch):

    query = """
    UNWIND $rows AS row

    MERGE (source:Person {id: row.source})
    MERGE (target:Person {id: row.target})

    CREATE (source)-[:FRIEND]->(target)
    """

    result = session.run(
        query,
        rows=batch
    )

    result.consume()


# ============================================================
# READ CSV
# ============================================================

print()
print("Starting dataset load...")

start_time = time.perf_counter()

batch = []

relationship_count = 0
batch_count = 0


with open(
    CSV_FILE,
    "r",
    encoding="utf-8",
    newline=""
) as file:

    reader = csv.DictReader(file)

    with driver.session() as session:

        for row in reader:

            batch.append({
                "source": int(row["source"]),
                "target": int(row["target"])
            })

            relationship_count += 1

            if len(batch) == BATCH_SIZE:

                load_batch(
                    session,
                    batch
                )

                batch_count += 1

                print(
                    f"Loaded "
                    f"{relationship_count:,} "
                    f"relationships..."
                )

                batch.clear()


        # ----------------------------------------------------
        # FINAL BATCH
        # ----------------------------------------------------

        if batch:

            load_batch(
                session,
                batch
            )

            batch_count += 1

            print(
                f"Loaded "
                f"{relationship_count:,} "
                f"relationships..."
            )


end_time = time.perf_counter()

load_time = end_time - start_time


# ============================================================
# VERIFY
# ============================================================

print()
print("=" * 60)
print("             DATABASE VERIFICATION")
print("=" * 60)

with driver.session() as session:

    node_count = session.run("""
        MATCH (n:Person)
        RETURN count(n) AS count
    """).single()["count"]

    relationship_count_db = session.run("""
        MATCH ()-[r:FRIEND]->()
        RETURN count(r) AS count
    """).single()["count"]


print()
print(f"CSV relationships       : {relationship_count:,}")
print(f"Database nodes          : {node_count:,}")
print(
    f"Database relationships  : "
    f"{relationship_count_db:,}"
)

print()
print(f"Number of batches       : {batch_count}")
print(f"Load time               : {load_time:.2f} seconds")


# ============================================================
# FINAL CHECK
# ============================================================

print()

if relationship_count_db == relationship_count:

    print(
        "✅ SUCCESS: All 100,000 relationships "
        "were loaded."
    )

else:

    print(
        "❌ ERROR: Database relationship count "
        "does not match CSV."
    )


driver.close()

print()
print("=" * 60)
print("                    FINISHED")
print("=" * 60)