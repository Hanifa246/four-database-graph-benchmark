import time
import statistics
import csv
from neo4j import GraphDatabase

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "MyNeo4jBenchmark2026!"

OUTPUT_FILE = "benchmark_results.csv"

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

queries = {
    "Q1_Count_Users": """
        MATCH (u:User)
        RETURN count(u) AS users
    """,

    "Q2_Count_Relationships": """
        MATCH ()-[r:KNOWS]->()
        RETURN count(r) AS relationships
    """,

    "Q3_One_Hop": """
        MATCH (u:User)-[:KNOWS]->(v:User)
        RETURN u.id, v.id
        LIMIT 100
    """,

    "Q4_Two_Hop": """
        MATCH (u:User)-[:KNOWS]->(v:User)-[:KNOWS]->(w:User)
        RETURN u.id, v.id, w.id
        LIMIT 100
    """,

    "Q5_Three_Hop": """
        MATCH (u:User)-[:KNOWS]->(v:User)
              -[:KNOWS]->(w:User)
              -[:KNOWS]->(x:User)
        RETURN u.id, v.id, w.id, x.id
        LIMIT 100
    """
}

RUNS = 10

results = []

try:
    driver.verify_connectivity()
    print("Connected to Neo4j!\n")

    with driver.session() as session:

        for name, query in queries.items():

            print("=" * 60)
            print(name)

            # Warm-up run
            session.run(query).consume()

            times = []

            for i in range(RUNS):

                start = time.perf_counter()

                result = session.run(query)
                result.consume()

                end = time.perf_counter()

                elapsed_ms = (end - start) * 1000
                times.append(elapsed_ms)

            average = statistics.mean(times)
            minimum = min(times)
            maximum = max(times)
            median = statistics.median(times)

            print(f"Runs       : {RUNS}")
            print(f"Average    : {average:.2f} ms")
            print(f"Minimum    : {minimum:.2f} ms")
            print(f"Maximum    : {maximum:.2f} ms")
            print(f"Median     : {median:.2f} ms")

            results.append({
                "Query": name,
                "Runs": RUNS,
                "Average_ms": round(average, 2),
                "Minimum_ms": round(minimum, 2),
                "Maximum_ms": round(maximum, 2),
                "Median_ms": round(median, 2)
            })

    # Save results
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
    print(f"Benchmark completed successfully!")
    print(f"Results saved to: {OUTPUT_FILE}")

finally:
    driver.close()