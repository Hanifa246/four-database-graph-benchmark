import time
import random
import threading
import csv
from pathlib import Path

from connectors.falkordb import create_falkordb_connector

OUTPUT_FILE = Path("results/mixed_falkordb_results.csv")

DURATION = 30
READ_RATIO = 0.8
WRITE_RATIO = 0.2

CONCURRENCIES = [1, 10, 40]


def worker(stop_event, stats):
    connector = create_falkordb_connector()

    reads = 0
    writes = 0
    errors = 0

    try:
        while not stop_event.is_set():

            try:
                if random.random() < READ_RATIO:

                    connector.run_query("""
                        MATCH (n:Node)
                        RETURN n.id
                        LIMIT 10
                    """)

                    reads += 1

                else:

                    node_id = random.randint(1, 169870)

                    connector.run_query(
                        """
                        MATCH (n:Node {id: $id})
                        SET n.benchmark_value = $value
                        """,
                        {
                            "id": node_id,
                            "value": random.randint(1, 1000000)
                        }
                    )

                    writes += 1

            except Exception:
                errors += 1

    finally:
        connector.close()

    stats["reads"] = reads
    stats["writes"] = writes
    stats["errors"] = errors


def run_test(concurrency):

    print()
    print("-" * 70)
    print(f"Concurrency: {concurrency}")

    stop_event = threading.Event()

    threads = []
    stats_list = []

    for _ in range(concurrency):

        stats = {
            "reads": 0,
            "writes": 0,
            "errors": 0
        }

        stats_list.append(stats)

        thread = threading.Thread(
            target=worker,
            args=(stop_event, stats)
        )

        threads.append(thread)

    start = time.perf_counter()

    for thread in threads:
        thread.start()

    time.sleep(DURATION)

    stop_event.set()

    for thread in threads:
        thread.join()

    elapsed = time.perf_counter() - start

    reads = sum(x["reads"] for x in stats_list)
    writes = sum(x["writes"] for x in stats_list)
    errors = sum(x["errors"] for x in stats_list)

    total = reads + writes

    throughput = total / elapsed

    print(f"Reads:        {reads:,}")
    print(f"Writes:       {writes:,}")
    print(f"Operations:   {total:,}")
    print(f"Errors:       {errors:,}")
    print(f"Duration:     {elapsed:.2f}s")
    print(f"Throughput:   {throughput:.2f} ops/s")

    return {
        "Database": "FalkorDB",
        "Concurrency": concurrency,
        "Duration_s": round(elapsed, 2),
        "Read_Ratio": READ_RATIO,
        "Write_Ratio": WRITE_RATIO,
        "Reads": reads,
        "Writes": writes,
        "Total_Operations": total,
        "Errors": errors,
        "Operations_per_second": round(throughput, 2)
    }


def main():

    print("=" * 70)
    print("FALKORDB MIXED WORKLOAD BENCHMARK")
    print("=" * 70)

    results = []

    for concurrency in CONCURRENCIES:
        results.append(run_test(concurrency))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
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
        )

        writer.writeheader()
        writer.writerows(results)

    print()
    print("=" * 70)
    print("FALKORDB MIXED WORKLOAD COMPLETE")
    print("=" * 70)

    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()