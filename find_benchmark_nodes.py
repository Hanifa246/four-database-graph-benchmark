import os
import csv
import random
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

OUTPUT_FILE = Path("data/benchmark_nodes.csv")

NUM_NODES = 10

RANDOM_SEED = 42

BATCH_SIZE = 10_000

# Minimum outgoing relationships required
MIN_DEGREE = 5


# ============================================================
# CONNECT
# ============================================================

print("=" * 60)
print("       FIND SUITABLE BENCHMARK STARTING NODES")
print("=" * 60)

print()
print("Connecting to CognoDB...")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

driver.verify_connectivity()

print("✅ Connected to CognoDB")


# ============================================================
# FIND CANDIDATE NODES
# ============================================================

print()
print(
    f"Finding nodes with at least "
    f"{MIN_DEGREE} outgoing relationships..."
)

candidate_nodes = []

skip = 0

with driver.session() as session:

    while True:

        print(
            f"Reading batch starting at "
            f"{skip:,}..."
        )

        result = session.run(
            """
            MATCH (p:Person)-[:FRIEND]->()
            WITH p, count(*) AS degree
            WHERE degree >= $min_degree
            RETURN p.id AS node_id, degree
            ORDER BY p.id
            SKIP $skip
            LIMIT $limit
            """,
            min_degree=MIN_DEGREE,
            skip=skip,
            limit=BATCH_SIZE
        )

        batch = [
            (
                record["node_id"],
                record["degree"]
            )
            for record in result
        ]

        if not batch:
            break

        candidate_nodes.extend(batch)

        print(
            f"  Retrieved "
            f"{len(batch):,} suitable nodes"
        )

        if len(batch) < BATCH_SIZE:
            break

        skip += BATCH_SIZE


# ============================================================
# CHECK CANDIDATES
# ============================================================

print()
print(
    f"Suitable nodes found: "
    f"{len(candidate_nodes):,}"
)

if len(candidate_nodes) < NUM_NODES:

    print()
    print(
        "❌ Not enough nodes with the "
        f"minimum degree of {MIN_DEGREE}."
    )

    driver.close()

    raise SystemExit(1)


# ============================================================
# REPRODUCIBLE RANDOM SELECTION
# ============================================================

random.seed(RANDOM_SEED)

selected_nodes = random.sample(
    candidate_nodes,
    NUM_NODES
)

selected_nodes.sort(
    key=lambda x: x[0]
)


# ============================================================
# DISPLAY
# ============================================================

print()
print("=" * 60)
print("             SELECTED NODES")
print("=" * 60)

print()

for node_id, degree in selected_nodes:

    print(
        f"Node: {node_id:<10} "
        f"Outgoing edges: {degree}"
    )


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "node_id",
        "outgoing_degree"
    ])

    for node_id, degree in selected_nodes:

        writer.writerow([
            node_id,
            degree
        ])


print()
print(
    "✅ Benchmark nodes saved to:"
)

print(
    OUTPUT_FILE.resolve()
)


# ============================================================
# CLOSE
# ============================================================

driver.close()

print()
print("=" * 60)
print("                    FINISHED")
print("=" * 60)