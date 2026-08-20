import csv
import random
import time
from pathlib import Path

from connectors.memgraph_connector import create_memgraph_connector
from benchmarks.statistics import calculate_statistics


DATA_FILE = Path(
    "data/processed/pokec_100k_edges.csv"
)

RANDOM_SEED = 42
RUNS = 100
WARMUP_RUNS = 20

random.seed(RANDOM_SEED)


def load_node_ids():

    nodes = set()

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            nodes.add(int(row["source"]))
            nodes.add(int(row["target"]))

    nodes = list(nodes)
    random.shuffle(nodes)

    return nodes


QUERY = """
MATCH (n:Node {id: $id})
RETURN n.id AS id
"""


def run_benchmark(connector, node_ids):

    selected_nodes = random.sample(
        node_ids,
        RUNS
    )

    # Warm-up
    for node_id in selected_nodes[:WARMUP_RUNS]:

        connector.run_query(
            QUERY,
            {"id": node_id}
        )

    latencies = []

    for node_id in selected_nodes:

        start = time.perf_counter()

        connector.run_query(
            QUERY,
            {"id": node_id}
        )

        end = time.perf_counter()

        latencies.append(
            (end - start) * 1000
        )

    return calculate_statistics(
        latencies
    )


def main():

    print("=" * 70)
    print("MEMGRAPH LOOKUP BENCHMARK")
    print("=" * 70)

    node_ids = load_node_ids()

    connector = create_memgraph_connector()

    try:

        connector.verify()

        print(
            f"Available nodes: {len(node_ids):,}"
        )

        print("Running indexed point lookup...")

        stats = run_benchmark(
            connector,
            node_ids
        )

        row = {
            "Database": "Memgraph",
            "Workload": "Indexed_Point_Lookup",
            "Runs": stats["runs"],
            "Average_ms": round(
                stats["average_ms"],
                4
            ),
            "Min_ms": round(
                stats["min_ms"],
                4
            ),
            "Max_ms": round(
                stats["max_ms"],
                4
            ),
            "P50_ms": round(
                stats["p50_ms"],
                4
            ),
            "P95_ms": round(
                stats["p95_ms"],
                4
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
        "lookup_memgraph_results.csv"
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
    print("MEMGRAPH LOOKUP COMPLETE")
    print(
        f"Results saved to: {output_file}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()