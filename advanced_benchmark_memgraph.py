import os
import time
import statistics
import csv

from dotenv import load_dotenv
from neo4j import GraphDatabase

# ---------------------------------------------------------
# LOAD MEMGRAPH CREDENTIALS
# ---------------------------------------------------------

load_dotenv()

USERNAME = os.getenv("MEMGRAPH_USERNAME")
PASSWORD = os.getenv("MEMGRAPH_PASSWORD")
HOST = os.getenv("MEMGRAPH_HOST")
PORT = os.getenv("MEMGRAPH_PORT")

URI = f"bolt+ssc://{HOST}:{PORT}"

OUTPUT_FILE = "memgraph_benchmark_results.csv"

RUNS = 20

# ---------------------------------------------------------
# EXACT SAME QUERIES USED FOR NEO4J
# ---------------------------------------------------------

queries = {

    "Node_Count": """
        MATCH (u:User)
        RETURN count(u)
    """,

    "Relationship_Count": """
        MATCH ()-[r:KNOWS]->()
        RETURN count(r)
    """,

    "One_Hop": """
        MATCH (u:User)-[:KNOWS]->(v:User)
        RETURN u.id, v.id
        LIMIT 100
    """,

    "Two_Hop": """
        MATCH (u:User)-[:KNOWS]->(v:User)-[:KNOWS]->(w:User)
        RETURN u.id, v.id, w.id
        LIMIT 100
    """,

    "Three_Hop": """
        MATCH (u:User)-[:KNOWS]->(v:User)
              -[:KNOWS]->(w:User)
              -[:KNOWS]->(x:User)
        RETURN u.id, v.id, w.id, x.id
        LIMIT 100
    """,

    "Degree_Query": """
        MATCH (u:User)-[:KNOWS]->(v:User)
        RETURN u.id, count(v) AS connections
        ORDER BY connections DESC
        LIMIT 100
    """
}

# ---------------------------------------------------------
# CONNECT TO MEMGRAPH
# ---------------------------------------------------------

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

results = []

try:

    print("=" * 60)
    print("MEMGRAPH ADVANCED BENCHMARK")
    print("=" * 60)

    print(f"Host : {HOST}")
    print(f"Port : {PORT}")
    print(f"Runs : {RUNS}")

    driver.verify_connectivity()

    print("\nConnected to Memgraph!\n")

    with driver.session() as session:

        for name, query in queries.items():

            print("=" * 60)
            print(name)

            # -------------------------------------------------
            # WARM-UP
            # -------------------------------------------------

            session.run(query).consume()

            times = []

            # -------------------------------------------------
            # 20 BENCHMARK RUNS
            # -------------------------------------------------

            for run in range(RUNS):

                start = time.perf_counter()

                result = session.run(query)
                result.consume()

                end = time.perf_counter()

                elapsed_ms = (end - start) * 1000

                times.append(elapsed_ms)

                print(
                    f"Run {run + 1:02d}: "
                    f"{elapsed_ms:.2f} ms"
                )

            # -------------------------------------------------
            # STATISTICS
            # -------------------------------------------------

            result_data = {
                "Query": name,
                "Runs": RUNS,
                "Average_ms": round(
                    statistics.mean(times), 2
                ),
                "Minimum_ms": round(
                    min(times), 2
                ),
                "Maximum_ms": round(
                    max(times), 2
                ),
                "Median_ms": round(
                    statistics.median(times), 2
                )
            }

            results.append(result_data)

            print("\nResults:")
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

    # ---------------------------------------------------------
    # SAVE CSV
    # ---------------------------------------------------------

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

    print("\n" + "=" * 60)
    print("MEMGRAPH BENCHMARK COMPLETED!")
    print("=" * 60)
    print(f"Results saved to: {OUTPUT_FILE}")

finally:

    driver.close()