import time
import statistics
import csv
from pathlib import Path

from connectors.falkordb import create_falkordb_connector

OUTPUT_FILE = Path("results/lookup_falkordb_results.csv")

WARMUP_RUNS = 20
MEASURED_RUNS = 100


def main():

    print("=" * 70)
    print("FALKORDB LOOKUP BENCHMARK")
    print("=" * 70)

    connector = create_falkordb_connector()

    try:
        print("Connected to FalkorDB.")

        # Get a valid node ID
        result = connector.run_query("""
            MATCH (n:Node)
            RETURN n.id
            LIMIT 1
        """)

        node_id = result[0][0]

        print(f"Lookup node: {node_id}")
        print("Running indexed point lookup...")

        query = """
            MATCH (n:Node {id: $id})
            RETURN n.id
        """

        parameters = {"id": node_id}

        # Warm-up
        for _ in range(WARMUP_RUNS):
            connector.run_query(query, parameters)

        times = []

        # Benchmark
        for _ in range(MEASURED_RUNS):

            start = time.perf_counter()

            connector.run_query(query, parameters)

            elapsed = (time.perf_counter() - start) * 1000

            times.append(elapsed)

        average = statistics.mean(times)
        p50 = statistics.median(times)
        p95 = sorted(times)[int(0.95 * len(times)) - 1]

        print(f"Average: {average:.4f} ms")
        print(f"P50:     {p50:.4f} ms")
        print(f"P95:     {p95:.4f} ms")

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
                    "Workload",
                    "Runs",
                    "Average_ms",
                    "Min_ms",
                    "Max_ms",
                    "P50_ms",
                    "P95_ms"
                ]
            )

            writer.writeheader()

            writer.writerow({
                "Database": "FalkorDB",
                "Workload": "Indexed_Point_Lookup",
                "Runs": MEASURED_RUNS,
                "Average_ms": round(average, 4),
                "Min_ms": round(min(times), 4),
                "Max_ms": round(max(times), 4),
                "P50_ms": round(p50, 4),
                "P95_ms": round(p95, 4)
            })

        print()
        print("=" * 70)
        print("FALKORDB LOOKUP COMPLETE")
        print("=" * 70)
        print(f"Results saved to: {OUTPUT_FILE}")

    finally:
        connector.close()


if __name__ == "__main__":
    main()