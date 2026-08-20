import csv
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from connectors.neo4j_connector import (
    create_cognodb_connector,
    create_aura_connector
)

DATA_FILE = Path("data/processed/pokec_100k_edges.csv")

RANDOM_SEED = 42
DURATION_SECONDS = 30

# Required concurrency sweep
CONCURRENCIES = [1, 10, 40]

# 80% reads / 20% writes
READ_RATIO = 0.80

random.seed(RANDOM_SEED)


def load_node_ids():
    """Load node IDs from the benchmark dataset."""

    node_ids = set()

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            node_ids.add(int(row["source"]))
            node_ids.add(int(row["target"]))

    return list(node_ids)


def execute_read(connector, node_id):
    """Simple indexed point lookup."""

    query = """
    MATCH (n:Node {id: $id})
    RETURN n.id AS id
    """

    connector.run_query(
        query,
        {"id": node_id}
    )


def execute_write(connector, node_id):
    """
    Small write workload.

    MERGE makes the operation idempotent so repeated benchmark
    executions do not continuously create duplicate relationships.
    """

    target_id = node_id

    query = """
    MERGE (n:Node {id: $id})
    SET n.benchmark_write = true
    """

    connector.run_query(
        query,
        {"id": target_id}
    )


def worker(connector, node_ids, end_time):
    """Run mixed read/write operations until the time limit."""

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
                f"Worker error: {type(error).__name__}: {error}"
            )

    return {
        "reads": reads,
        "writes": writes,
        "errors": errors
    }


def run_mixed_workload(
    database_name,
    connector_factory,
    node_ids,
    concurrency
):

    print()
    print("=" * 70)
    print(
        f"{database_name} | "
        f"Concurrency={concurrency}"
    )
    print("=" * 70)

    # Create one connector per worker so each worker has
    # its own Neo4j driver/session context.
    connectors = [
        connector_factory()
        for _ in range(concurrency)
    ]

    try:

        for connector in connectors:
            connector.verify()

        print(
            f"Duration: {DURATION_SECONDS} seconds"
        )

        print(
            f"Read/write mix: "
            f"{int(READ_RATIO * 100)}% read / "
            f"{int((1 - READ_RATIO) * 100)}% write"
        )

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

            for future in as_completed(futures):

                results.append(
                    future.result()
                )

        elapsed = (
            time.perf_counter() -
            start_time
        )

        total_reads = sum(
            result["reads"]
            for result in results
        )

        total_writes = sum(
            result["writes"]
            for result in results
        )

        total_errors = sum(
            result["errors"]
            for result in results
        )

        total_operations = (
            total_reads +
            total_writes
        )

        throughput = (
            total_operations / elapsed
            if elapsed > 0
            else 0
        )

        print()
        print(
            f"Total reads:       {total_reads:,}"
        )

        print(
            f"Total writes:      {total_writes:,}"
        )

        print(
            f"Total operations:  {total_operations:,}"
        )

        print(
            f"Errors:            {total_errors:,}"
        )

        print(
            f"Elapsed:           {elapsed:.2f} seconds"
        )

        print(
            f"Throughput:        "
            f"{throughput:.2f} operations/sec"
        )

        return {
            "Database": database_name,
            "Concurrency": concurrency,
            "Duration_s": round(elapsed, 2),
            "Read_Ratio": READ_RATIO,
            "Write_Ratio": 1 - READ_RATIO,
            "Reads": total_reads,
            "Writes": total_writes,
            "Total_Operations": total_operations,
            "Errors": total_errors,
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
    print("WEXA MIXED READ/WRITE BENCHMARK")
    print("=" * 70)

    node_ids = load_node_ids()

    print(
        f"Available nodes: {len(node_ids):,}"
    )

    databases = {
        "CognoDB": create_cognodb_connector,
        "Neo4j_Aura": create_aura_connector
    }

    results = []

    for database_name, connector_factory in databases.items():

        for concurrency in CONCURRENCIES:

            result = run_mixed_workload(
                database_name,
                connector_factory,
                node_ids,
                concurrency
            )

            results.append(result)

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    output_file = (
        output_dir /
        "mixed_workload_results.csv"
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
    print("MIXED WORKLOAD COMPLETE")
    print(
        f"Results saved to: {output_file}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()