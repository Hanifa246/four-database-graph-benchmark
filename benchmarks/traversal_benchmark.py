import random
import csv
from pathlib import Path

from connectors.neo4j_connector import (
    create_cognodb_connector,
    create_aura_connector
)

from benchmarks.runner import benchmark

from benchmarks.statistics import calculate_statistics
DATA_FILE = Path("data/processed/pokec_100k_edges.csv")

RANDOM_SEED = 42
RUNS = 100
WARMUP_RUNS = 20

random.seed(RANDOM_SEED)


def load_start_nodes():
    nodes = set()

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            nodes.add(int(row["source"]))
            nodes.add(int(row["target"]))

    nodes = list(nodes)

    random.shuffle(nodes)

    return nodes


def create_query(hops):

    if hops == 1:
        return """
        MATCH (start:Node {id: $start_id})
              -[:CONNECTED_TO*1..1]-(n)
        RETURN count(n) AS result
        """

    if hops == 2:
        return """
        MATCH (start:Node {id: $start_id})
              -[:CONNECTED_TO*2..2]-(n)
        RETURN count(DISTINCT n) AS result
        """

    if hops == 3:
        return """
        MATCH (start:Node {id: $start_id})
              -[:CONNECTED_TO*3..3]-(n)
        RETURN count(DISTINCT n) AS result
        """

    raise ValueError("Unsupported hop count")


def run_traversal(connector, hops, start_nodes):

    query = create_query(hops)

    # Select 100 different start nodes
    selected_nodes = random.sample(
        start_nodes,
        RUNS
    )

    # Warm-up using the first 20 nodes
    for start_id in selected_nodes[:WARMUP_RUNS]:

        connector.run_query(
            query,
            {"start_id": start_id}
        )

    # Measure 100 different start nodes
    latencies = []

    import time

    for start_id in selected_nodes:

        start_time = time.perf_counter()

        connector.run_query(
            query,
            {"start_id": start_id}
        )

        end_time = time.perf_counter()

        latency_ms = (
            end_time - start_time
        ) * 1000

        latencies.append(latency_ms)

    from benchmarks.statistics import calculate_statistics

    return calculate_statistics(latencies)


def main():

    print("=" * 70)
    print("WEXA GRAPH DATABASE TRAVERSAL BENCHMARK")
    print("=" * 70)

    start_nodes = load_start_nodes()

    print(
        f"Available start nodes: "
        f"{len(start_nodes):,}"
    )

    print(f"Warm-up runs: {WARMUP_RUNS}")
    print(f"Measured runs: {RUNS}")
    print()

    databases = {
        "CognoDB": create_cognodb_connector(),
        "Neo4j_Aura": create_aura_connector()
    }

    results = []

    try:

        for database_name, connector in databases.items():

            print("-" * 70)
            print(database_name)
            print("-" * 70)

            connector.verify()

            for hops in [1, 2, 3]:

                print(
                    f"Running {hops}-hop..."
                )

                stats = run_traversal(
                    connector,
                    hops,
                    start_nodes
                )

                row = {
                    "Database": database_name,
                    "Workload": f"{hops}-Hop",
                    "Runs": stats["runs"],
                    "Average_ms": round(
                        stats["average_ms"], 4
                    ),
                    "Min_ms": round(
                        stats["min_ms"], 4
                    ),
                    "Max_ms": round(
                        stats["max_ms"], 4
                    ),
                    "P50_ms": round(
                        stats["p50_ms"], 4
                    ),
                    "P95_ms": round(
                        stats["p95_ms"], 4
                    )
                }

                results.append(row)

                print(
                    f"Average: {row['Average_ms']} ms"
                )

                print(
                    f"P50:     {row['P50_ms']} ms"
                )

                print(
                    f"P95:     {row['P95_ms']} ms"
                )

                print()

    finally:

        for connector in databases.values():
            connector.close()

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    output_file = (
        output_dir /
        "traversal_results.csv"
    )

    fieldnames = [
        "Database",
        "Workload",
        "Runs",
        "Average_ms",
        "Min_ms",
        "Max_ms",
        "P50_ms",
        "P95_ms"
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

    print("=" * 70)
    print("TRAVERSAL BENCHMARK COMPLETE")
    print(
        f"Results saved to: {output_file}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()