import os
import time
import statistics
import csv

from dotenv import load_dotenv
from neo4j import GraphDatabase


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

OUTPUT_FILE = "advanced_benchmark_cognodb_results.csv"

RUNS = 20


# ============================================================
# VALIDATION
# ============================================================

if not URI:
    raise ValueError("COGNODB_URI is missing from .env")

if not USERNAME:
    raise ValueError("COGNODB_USERNAME is missing from .env")

if not PASSWORD:
    raise ValueError("COGNODB_PASSWORD is missing from .env")


# ============================================================
# QUERIES
# Same operations as Neo4j advanced benchmark
# ============================================================

queries = {

    "Node_Count": """
        MATCH (u:Person)
        RETURN count(u)
    """,

    "Relationship_Count": """
        MATCH ()-[r:FRIEND]->()
        RETURN count(r)
    """,

    "One_Hop": """
        MATCH (u:Person)-[:FRIEND]->(v:Person)
        RETURN u.id, v.id
        LIMIT 100
    """,

    "Two_Hop": """
        MATCH (u:Person)-[:FRIEND]->(v:Person)
              -[:FRIEND]->(w:Person)
        RETURN u.id, v.id, w.id
        LIMIT 100
    """,

    "Three_Hop": """
        MATCH (u:Person)-[:FRIEND]->(v:Person)
              -[:FRIEND]->(w:Person)
              -[:FRIEND]->(x:Person)
        RETURN u.id, v.id, w.id, x.id
        LIMIT 100
    """,

    "Degree_Query": """
        MATCH (u:Person)-[:FRIEND]->(v:Person)
        RETURN u.id, count(v) AS connections
        ORDER BY connections DESC
        LIMIT 100
    """
}


# ============================================================
# CONNECT
# ============================================================

print("=" * 60)
print("        COGNODB ADVANCED BENCHMARK")
print("=" * 60)

print()

print("Connecting to CognoDB...")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


results = []


try:

    driver.verify_connectivity()

    print("Connected to CognoDB!")
    print()

    # ========================================================
    # DATABASE CHECK
    # ========================================================

    print("Checking database...")

    with driver.session() as session:

        node_count = session.run("""
            MATCH (u:Person)
            RETURN count(u) AS count
        """).single()["count"]

        relationship_count = session.run("""
            MATCH ()-[r:FRIEND]->()
            RETURN count(r) AS count
        """).single()["count"]

    print(f"Nodes         : {node_count:,}")
    print(f"Relationships : {relationship_count:,}")

    print()

    # ========================================================
    # RUN BENCHMARK
    # ========================================================

    for name, query in queries.items():

        print("=" * 60)
        print(name)

        # Warm-up
        with driver.session() as session:
            session.run(query).consume()

        times = []

        for _ in range(RUNS):

            with driver.session() as session:

                start = time.perf_counter()

                result = session.run(query)

                result.consume()

                end = time.perf_counter()

            elapsed_ms = (end - start) * 1000

            times.append(elapsed_ms)

        result_data = {

            "Query": name,

            "Runs": RUNS,

            "Average_ms": round(
                statistics.mean(times),
                2
            ),

            "Minimum_ms": round(
                min(times),
                2
            ),

            "Maximum_ms": round(
                max(times),
                2
            ),

            "Median_ms": round(
                statistics.median(times),
                2
            )
        }

        results.append(result_data)

        print(
            f"Average : "
            f"{result_data['Average_ms']} ms"
        )

        print(
            f"Minimum : "
            f"{result_data['Minimum_ms']} ms"
        )

        print(
            f"Maximum : "
            f"{result_data['Maximum_ms']} ms"
        )

        print(
            f"Median  : "
            f"{result_data['Median_ms']} ms"
        )


    # ========================================================
    # SAVE RESULTS
    # ========================================================

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "Query",
                "Runs",
                "Average_ms",
                "Minimum_ms",
                "Maximum_ms",
                "Median_ms"
            ]
        )

        writer.writeheader()

        writer.writerows(results)


    # ========================================================
    # DISPLAY FINAL RESULTS
    # ========================================================

    print()
    print("=" * 60)
    print("        COGNODB BENCHMARK RESULTS")
    print("=" * 60)

    print()

    for result in results:

        print(
            f"{result['Query']:<20}"
            f"{result['Average_ms']:>10.2f} ms"
        )

    print()

    print("=" * 60)
    print("Benchmark completed successfully!")
    print(
        f"Results saved to: "
        f"{OUTPUT_FILE}"
    )
    print("=" * 60)


finally:

    driver.close()