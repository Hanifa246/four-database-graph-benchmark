import time
import csv
from pathlib import Path

from connectors.memgraph_connector import create_memgraph_connector
from benchmarks.statistics import calculate_statistics


RUNS = 100
WARMUP_RUNS = 20

QUERY = """
MATCH (n:Node)
RETURN count(n) AS node_count
"""


def run_benchmark(connector):

    # Warm-up
    for _ in range(WARMUP_RUNS):
        connector.run_query(QUERY)

    latencies = []

    for _ in range(RUNS):

        start = time.perf_counter()

        result = connector.run_query(QUERY)

        end = time.perf_counter()

        if not result:
            raise RuntimeError(
                "Aggregation query returned no result."
            )

        latencies.append(
            (end - start) * 1000
        )

    return calculate_statistics(latencies)


def main():

    print("=" * 70)
    print("MEMGRAPH AGGREGATION BENCHMARK")
    print("=" * 70)

    connector = create_memgraph_connector()

    try:

        connector.verify()

        print("Running node count aggregation...")

        stats = run_benchmark(connector)

        row = {
            "Database": "Memgraph",
            "Workload": "Node_Count_Aggregation",
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

        print(
            f"Average: {row['Average_ms']} ms"
        )

        print(
            f"P50:     {row['P50_ms']} ms"
        )

        print(
            f"P95:     {row['P95_ms']} ms"
        )

    finally:

        connector.close()

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    output_file = (
        output_dir /
        "aggregation_memgraph_results.csv"
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
        writer.writerow(row)

    print()
    print("=" * 70)
    print("MEMGRAPH AGGREGATION COMPLETE")
    print(
        f"Results saved to: {output_file}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()