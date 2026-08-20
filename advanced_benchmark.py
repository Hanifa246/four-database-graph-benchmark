import time
import statistics
import csv
from neo4j import GraphDatabase

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "MyNeo4jBenchmark2026!"

OUTPUT_FILE = "advanced_benchmark_results.csv"

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

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

RUNS = 20

results = []

try:
    driver.verify_connectivity()
    print("Connected to Neo4j!\n")

    with driver.session() as session:

        for name, query in queries.items():

            print("=" * 60)
            print(name)

            # Warm-up
            session.run(query).consume()

            times = []

            for _ in range(RUNS):

                start = time.perf_counter()

                result = session.run(query)
                result.consume()

                end = time.perf_counter()

                times.append((end - start) * 1000)

            result_data = {
                "Query": name,
                "Runs": RUNS,
                "Average_ms": round(statistics.mean(times), 2),
                "Minimum_ms": round(min(times), 2),
                "Maximum_ms": round(max(times), 2),
                "Median_ms": round(statistics.median(times), 2)
            }

            results.append(result_data)

            print(f"Average : {result_data['Average_ms']} ms")
            print(f"Minimum : {result_data['Minimum_ms']} ms")
            print(f"Maximum : {result_data['Maximum_ms']} ms")
            print(f"Median  : {result_data['Median_ms']} ms")

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
    print("Advanced benchmark completed!")
    print(f"Results saved to: {OUTPUT_FILE}")

finally:
    driver.close()