import os
import csv
import time
import statistics
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from arango import ArangoClient


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

ARANGO_HOST = os.getenv("ARANGO_HOST", "http://localhost:8529")
ARANGO_USERNAME = os.getenv("ARANGO_USERNAME", "root")

# Support both names so the benchmark works with the existing .env
ARANGO_PASSWORD = (
    os.getenv("ARANGO_PASSWORD")
    or os.getenv("ARANGODB_PASSWORD")
)

DATABASE_NAME = os.getenv("ARANGO_DATABASE", "_system")

GRAPH_NAME = "pokec_graph"
NODE_COLLECTION = "nodes"
EDGE_COLLECTION = "relationships"

DATASET_NODES = 169870
DATASET_EDGES = 100000

LATENCY_RUNS = 100
WARMUP_RUNS = 10

MIXED_DURATION_SECONDS = 30
CONCURRENCY_LEVELS = [1, 10, 40]

READ_PERCENTAGE = 80
WRITE_PERCENTAGE = 20

LATENCY_OUTPUT = "arangodb_benchmark_results.csv"
MIXED_OUTPUT = "arangodb_mixed_workload_results.csv"


# ============================================================
# CONNECTION
# ============================================================

def connect_arangodb():
    if not ARANGO_PASSWORD:
        raise ValueError(
            "ARANGO_PASSWORD or ARANGODB_PASSWORD is not set in .env"
        )

    client = ArangoClient(hosts=ARANGO_HOST)

    db = client.db(
        DATABASE_NAME,
        username=ARANGO_USERNAME,
        password=ARANGO_PASSWORD
    )

    # Verify connection
    version = db.version()

    print("=" * 70)
    print("ARANGODB BENCHMARK")
    print("=" * 70)
    print(f"Host:     {ARANGO_HOST}")
    print(f"Database: {DATABASE_NAME}")
    print(f"Version:  {version}")
    print("=" * 70)

    return client, db


# ============================================================
# VERIFY DATA
# ============================================================

def verify_database(db):
    print("VERIFYING ARANGODB DATA")
    print("-" * 70)

    if not db.has_collection(NODE_COLLECTION):
        raise RuntimeError(
            f"Collection '{NODE_COLLECTION}' does not exist"
        )

    if not db.has_collection(EDGE_COLLECTION):
        raise RuntimeError(
            f"Collection '{EDGE_COLLECTION}' does not exist"
        )

    if not db.has_graph(GRAPH_NAME):
        raise RuntimeError(
            f"Graph '{GRAPH_NAME}' does not exist"
        )

    node_count = db.collection(NODE_COLLECTION).count()
    edge_count = db.collection(EDGE_COLLECTION).count()

    print(f"Nodes:         {node_count}")
    print(f"Relationships: {edge_count}")

    if node_count != DATASET_NODES:
        print(
            f"WARNING: expected {DATASET_NODES} nodes, "
            f"found {node_count}"
        )

    if edge_count != DATASET_EDGES:
        print(
            f"WARNING: expected {DATASET_EDGES} relationships, "
            f"found {edge_count}"
        )

    print("-" * 70)


# ============================================================
# TEST NODE
# ============================================================

def get_test_node(db):
    cursor = db.aql.execute(
        f"""
        FOR doc IN `{NODE_COLLECTION}`
            LIMIT 1
            RETURN doc._key
        """
    )

    for key in cursor:
        return str(key)

    raise RuntimeError("No nodes found in ArangoDB")


# ============================================================
# BENCHMARK QUERIES
# ============================================================

def node_count_query(db):
    cursor = db.aql.execute(
        f"""
        RETURN LENGTH(
            FOR doc IN `{NODE_COLLECTION}`
                RETURN 1
        )
        """
    )

    return next(cursor)


def relationship_count_query(db):
    cursor = db.aql.execute(
        f"""
        RETURN LENGTH(
            FOR edge IN `{EDGE_COLLECTION}`
                RETURN 1
        )
        """
    )

    return next(cursor)


def indexed_lookup_query(db, node_key):
    collection = db.collection(NODE_COLLECTION)

    return collection.get(node_key)


def traversal_query(db, node_key, depth):
    cursor = db.aql.execute(
        f"""
        FOR v, e, p IN 1..{depth}
            OUTBOUND @start
            GRAPH '{GRAPH_NAME}'
            OPTIONS {{
                uniqueVertices: "path",
                uniqueEdges: "path"
            }}
            LIMIT 100
            RETURN v._key
        """,
        bind_vars={
            "start": f"{NODE_COLLECTION}/{node_key}"
        }
    )

    return list(cursor)


# ============================================================
# TIMING
# ============================================================

def measure(function, runs=LATENCY_RUNS):
    # Warm-up
    for _ in range(WARMUP_RUNS):
        try:
            function()
        except Exception:
            pass

    samples = []

    for _ in range(runs):
        start = time.perf_counter()

        function()

        elapsed = (time.perf_counter() - start) * 1000
        samples.append(elapsed)

    return {
        "runs": len(samples),
        "average_ms": statistics.mean(samples),
        "minimum_ms": min(samples),
        "maximum_ms": max(samples),
        "median_ms": statistics.median(samples),
        "p95_ms": percentile(samples, 95)
    }


def percentile(values, percentile_value):
    values = sorted(values)

    if not values:
        return 0

    index = (len(values) - 1) * percentile_value / 100

    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    if lower == upper:
        return values[lower]

    fraction = index - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * fraction
    )


# ============================================================
# LATENCY BENCHMARK
# ============================================================

def run_latency_benchmark(db, node_key):

    workloads = {
        "Node_Count": lambda: node_count_query(db),

        "Relationship_Count":
            lambda: relationship_count_query(db),

        "Indexed_Lookup":
            lambda: indexed_lookup_query(db, node_key),

        "One_Hop":
            lambda: traversal_query(db, node_key, 1),

        "Two_Hop":
            lambda: traversal_query(db, node_key, 2),

        "Three_Hop":
            lambda: traversal_query(db, node_key, 3),
    }

    results = []

    print()
    print("=" * 70)
    print("LATENCY BENCHMARK")
    print("=" * 70)

    for name, function in workloads.items():

        print()
        print(f"Running {name}...")

        stats = measure(function)

        print(f"Average: {stats['average_ms']:.4f} ms")
        print(f"Minimum: {stats['minimum_ms']:.4f} ms")
        print(f"Maximum: {stats['maximum_ms']:.4f} ms")
        print(f"Median:  {stats['median_ms']:.4f} ms")
        print(f"P95:     {stats['p95_ms']:.4f} ms")

        results.append({
            "Database": "ArangoDB",
            "Query": name,
            "Runs": stats["runs"],
            "Average_ms": round(stats["average_ms"], 4),
            "Minimum_ms": round(stats["minimum_ms"], 4),
            "Maximum_ms": round(stats["maximum_ms"], 4),
            "Median_ms": round(stats["median_ms"], 4),
            "P95_ms": round(stats["p95_ms"], 4)
        })

    return results


# ============================================================
# MIXED WORKLOAD
# ============================================================

def mixed_read(db, node_key):
    operation = random.randint(1, 4)

    if operation == 1:
        return indexed_lookup_query(db, node_key)

    if operation == 2:
        return traversal_query(db, node_key, 1)

    if operation == 3:
        return traversal_query(db, node_key, 2)

    return traversal_query(db, node_key, 3)


def mixed_write(db, node_key):
    collection = db.collection(NODE_COLLECTION)

    collection.update(
        {
            "_key": node_key,
            "benchmark_updated": time.time()
        },
        merge=True
    )


def mixed_worker(db, node_key, end_time, counter):
    while time.perf_counter() < end_time:

        choice = random.randint(1, 100)

        if choice <= READ_PERCENTAGE:
            mixed_read(db, node_key)
        else:
            mixed_write(db, node_key)

        counter[0] += 1


def run_mixed_for_connection(db, node_key, workers):

    counter = [0]

    end_time = (
        time.perf_counter()
        + MIXED_DURATION_SECONDS
    )

    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=workers) as executor:

        futures = [
            executor.submit(
                mixed_worker,
                db,
                node_key,
                end_time,
                counter
            )
            for _ in range(workers)
        ]

        for future in as_completed(futures):
            future.result()

    elapsed = time.perf_counter() - start

    operations = counter[0]

    throughput = operations / elapsed if elapsed > 0 else 0

    return operations, elapsed, throughput


def run_mixed_benchmark(db, node_key):

    print()
    print("=" * 70)
    print("MIXED READ/WRITE WORKLOAD")
    print("=" * 70)

    print(
        f"Workload: {READ_PERCENTAGE}% reads / "
        f"{WRITE_PERCENTAGE}% writes"
    )

    print(
        f"Duration: {MIXED_DURATION_SECONDS} seconds"
    )

    results = []

    for workers in CONCURRENCY_LEVELS:

        print()
        print(f"Concurrency: {workers}")

        operations, elapsed, throughput = (
            run_mixed_for_connection(
                db,
                node_key,
                workers
            )
        )

        print(f"Operations: {operations}")
        print(f"Elapsed:    {elapsed:.2f} seconds")
        print(f"Throughput: {throughput:.2f} ops/sec")

        results.append({
            "Database": "ArangoDB",
            "Concurrency": workers,
            "Duration_seconds": round(elapsed, 2),
            "Operations": operations,
            "Throughput_ops_sec": round(
                throughput,
                2
            ),
            "Read_Percentage": READ_PERCENTAGE,
            "Write_Percentage": WRITE_PERCENTAGE
        })

    return results


# ============================================================
# CSV OUTPUT
# ============================================================

def save_latency_results(results):

    fieldnames = [
        "Database",
        "Query",
        "Runs",
        "Average_ms",
        "Minimum_ms",
        "Maximum_ms",
        "Median_ms",
        "P95_ms"
    ]

    with open(
        LATENCY_OUTPUT,
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
    print(f"Latency results saved to: {LATENCY_OUTPUT}")


def save_mixed_results(results):

    fieldnames = [
        "Database",
        "Concurrency",
        "Duration_seconds",
        "Operations",
        "Throughput_ops_sec",
        "Read_Percentage",
        "Write_Percentage"
    ]

    with open(
        MIXED_OUTPUT,
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

    print(
        f"Mixed workload results saved to: "
        f"{MIXED_OUTPUT}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("ARANGODB GRAPH DATABASE BENCHMARK")
    print("=" * 70)

    client = None

    try:

        client, db = connect_arangodb()

        verify_database(db)

        node_key = get_test_node(db)

        print(f"Test node: {node_key}")

        latency_results = run_latency_benchmark(
            db,
            node_key
        )

        save_latency_results(
            latency_results
        )

        mixed_results = run_mixed_benchmark(
            db,
            node_key
        )

        save_mixed_results(
            mixed_results
        )

        print()
        print("=" * 70)
        print("ARANGODB BENCHMARK COMPLETE")
        print("=" * 70)

        print()
        print("Generated files:")
        print(f"  {LATENCY_OUTPUT}")
        print(f"  {MIXED_OUTPUT}")

    except Exception as error:

        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)
        print(error)

        raise

    finally:

        if client is not None:
            try:
                client.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()