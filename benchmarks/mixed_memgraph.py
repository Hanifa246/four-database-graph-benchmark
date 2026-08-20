import csv
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from connectors.memgraph_connector import create_memgraph_connector


DATA_FILE = Path(
    "data/processed/pokec_100k_edges.csv"
)

RANDOM_SEED = 42
DURATION_SECONDS = 30

CONCURRENCIES = [1, 10, 40]

READ_RATIO = 0.80

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

    return list(nodes)


def execute_read(connector, node_id):

    query = """
    MATCH (n:Node {id: $id})
    RETURN n.id AS id
    """

    connector.run_query(
        query,
        {"id": node_id}
    )


def execute_write(connector, node_id):

    query = """
    MATCH (n:Node {id: $id})
    SET n.benchmark_write = true
    RETURN n.id AS id
    """

    connector.run_query(
        query,
        {"id": node_id}
    )


def worker(
    connector,
    node_ids,
    end_time
):

    reads = 0
    writes = 0
    errors = 0

    while time.perf_counter() < end_time:

        node_id = random.choice(node_ids)

        try:

            if random.random() < READ_RATIO:

                execute_read(
                    connector,
                    node_id
                )

                reads += 1

            else:

                execute_write(
                    connector,
                    node_id
                )

                writes += 1

        except Exception as error:

            errors += 1

            print(
                f"Worker error: "
                f"{type(error).__name__}: {error}"
            )

    return {
        "reads": reads,
        "writes": writes,
        "errors": errors
    }


def run_workload(
    node_ids,
    concurrency
):

    print()
    print("=" * 70)
    print(
        f"Memgraph | "
        f"Concurrency={concurrency}"
    )
    print("=" * 70)

    connectors = [
        create_memgraph_connector()
        for _ in range(concurrency)
    ]

    try:

        for connector in connectors:
            connector.verify()

        start_time = time.perf_counter()

        end_time = (
            start_time +
            DURATION_SECONDS
        )

        results = []

        with ThreadPoolExecutor(
            max_workers=concurrency
        ) as executor:

            futures = []

            for connector in connectors:

                futures.append(
                    executor.submit(
                        worker,
                        connector,
                        node_ids,
                        end_time
                    )
                )

            for future in as_completed(
                futures
            ):

                results.append(
                    future.result()
                )

        elapsed = (
            time.perf_counter()
            - start_time
        )

        reads = sum(
            r["reads"]
            for r in results
        )

        writes = sum(
            r["writes"]
            for r in results
        )

        errors = sum(
            r["errors"]
            for r in results
        )

        total = reads + writes

        throughput = (
            total / elapsed
            if elapsed > 0
            else 0
        )

        print(
            f"Reads:        {reads:,}"
        )

        print(
            f"Writes:       {writes:,}"
        )

        print(
            f"Operations:   {total:,}"
        )

        print(
            f"Errors:       {errors:,}"
        )

        print(
            f"Duration:     {elapsed:.2f}s"
        )

        print(
            f"Throughput:   "
            f"{throughput:.2f} ops/s"
        )

        return {
            "Database": "Memgraph",
            "Concurrency": concurrency,
            "Duration_s": round(
                elapsed,
                2
            ),
            "Read_Ratio": READ_RATIO,
            "Write_Ratio": 1 - READ_RATIO,
            "Reads": reads,
            "Writes": writes,
            "Total_Operations": total,
            "Errors": errors,
            "Operations_per_second": round(
                throughput,
                2
            )
        }

    finally:

        for connector in connectors:
            connector.close()


def main():

    print("=" * 70)
    print("MEMGRAPH MIXED WORKLOAD BENCHMARK")
    print("=" * 70)

    node_ids = load_node_ids()

    print(
        f"Available nodes: "
        f"{len(node_ids):,}"
    )

    results = []

    for concurrency in CONCURRENCIES:

        results.append(
            run_workload(
                node_ids,
                concurrency
            )
        )

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    output_file = (
        output_dir /
        "mixed_memgraph_results.csv"
    )

    fieldnames = [
        "Database",
        "Concurrency",
        "Duration_s",
        "Read_Ratio",
        "Write_Ratio",
        "Reads",
        "Writes",
        "Total_Operations",
        "Errors",
        "Operations_per_second"
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

    print()
    print("=" * 70)
    print("MEMGRAPH MIXED WORKLOAD COMPLETE")
    print(
        f"Results saved to: {output_file}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()