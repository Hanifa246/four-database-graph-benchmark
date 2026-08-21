import os
import time
import statistics
import csv
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from arango import ArangoClient


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

ARANGO_HOST = os.getenv("ARANGO_HOST", "http://localhost:8529")
ARANGO_USERNAME = os.getenv("ARANGO_USERNAME", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD")

DATABASE_NAME = "_system"
GRAPH_NAME = "pokec_graph"

NODE_COLLECTION = "nodes"
EDGE_COLLECTION = "relationships"

RUNS = 100
WARMUP_RUNS = 10

MIXED_DURATION = 30
CONCURRENCY_LEVELS = [1, 10, 40]

OUTPUT_DIR = Path("results")
OUTPUT_DIR.mkdir(exist_ok=True)

LATENCY_OUTPUT = OUTPUT_DIR / "arangodb_benchmark_results.csv"
MIXED_OUTPUT = OUTPUT_DIR / "arangodb_mixed_workload_results.csv"


# ============================================================
# CONNECTION
# ============================================================

def connect_arangodb():

    if not ARANGO_PASSWORD:
        raise ValueError(
            "ARANGO_PASSWORD is not set in the .env file"
        )

    client = ArangoClient(hosts=ARANGO_HOST)

    db = client.db(
        DATABASE_NAME,
        username=ARANGO_USERNAME,
        password=ARANGO_PASSWORD
    )

    return client, db


# ============================================================
# SERVER VERSION
# ============================================================

def get_server_version(db):

    try:
        return db.version
    except Exception:
        return "Unknown"


QUERIES = {
    "Node_Count": """
        RETURN LENGTH(@@nodes)
    """,

    "Relationship_Count": """
        RETURN LENGTH(@@edges)
    """,

    "Indexed_Lookup": """
        FOR n IN @@nodes
            FILTER n._key == @node_id
            LIMIT 1
            RETURN n
    """,

    "One_Hop": """
        FOR v, e IN 1..1 OUTBOUND @start_vertex @@edges
            RETURN v
    """,

    "Two_Hop": """
        FOR v, e, p IN 2..2 OUTBOUND @start_vertex @@edges
            RETURN v
    """,

    "Three_Hop": """
        FOR v, e, p IN 3..3 OUTBOUND @start_vertex @@edges
            RETURN v
    """
}


# ============================================================
# FIND TEST NODE
# ============================================================

def find_test_node(db):

    cursor = db.aql.execute(
        f"""
        FOR n IN `{NODE_COLLECTION}`
            LIMIT 1
            RETURN n._key
        """
    )

    result = list(cursor)

    if not result:
        raise RuntimeError(
            "No nodes found in ArangoDB"
        )

    return result[0]


# ============================================================
# RUN QUERY
# ============================================================

def run_query(db, query, bind_vars):

    start = time.perf_counter()

    cursor = db.aql.execute(
        query,
        bind_vars=bind_vars
    )

    # Consume complete cursor
    list(cursor)

    end = time.perf_counter()

    return (end - start) * 1000


# ============================================================
# P95
# ============================================================

def calculate_p95(values):

    sorted_values = sorted(values)

    index = int(
        0.95 * len(sorted_values)
    ) - 1

    index = max(
        0,
        min(index, len(sorted_values) - 1)
    )

    return sorted_values[index]


# ============================================================
# BENCHMARK ONE QUERY
# ============================================================

def benchmark_query(
    db,
    query_name,
    query,
    bind_vars
):

    print()
    print("-" * 60)
    print(f"Running {query_name}")

    # --------------------------------------------------------
    # WARM-UP
    # --------------------------------------------------------

    print(
        f"Warm-up runs: {WARMUP_RUNS}"
    )

    for _ in range(WARMUP_RUNS):

        run_query(
            db,
            query,
            bind_vars
        )

    # --------------------------------------------------------
    # BENCHMARK
    # --------------------------------------------------------

    print(
        f"Benchmark runs: {RUNS}"
    )

    times = []

    for i in range(RUNS):

        elapsed = run_query(
            db,
            query,
            bind_vars
        )

        times.append(elapsed)

        if (i + 1) % 20 == 0:

            print(
                f"Completed {i + 1}/{RUNS}"
            )

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    average = statistics.mean(times)
    minimum = min(times)
    maximum = max(times)
    median = statistics.median(times)
    p95 = calculate_p95(times)

    print()
    print(
        f"Average: {average:.4f} ms"
    )

    print(
        f"Minimum: {minimum:.4f} ms"
    )

    print(
        f"Maximum: {maximum:.4f} ms"
    )

    print(
        f"Median:  {median:.4f} ms"
    )

    print(
        f"P95:     {p95:.4f} ms"
    )

    return {

        "Database": "ArangoDB",

        "Query": query_name,

        "Runs": RUNS,

        "Average_ms":
            round(average, 4),

        "Minimum_ms":
            round(minimum, 4),

        "Maximum_ms":
            round(maximum, 4),

        "Median_ms":
            round(median, 4),

        "P95_ms":
            round(p95, 4)
    }


# ============================================================
# SAVE LATENCY RESULTS
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


# ============================================================
# MIXED WORKLOAD OPERATION
# ============================================================

def mixed_operation(
    db,
    node_id,
    operation_number
):

    # 80% reads
    # 20% writes

    if random.random() < 0.80:

        query = f"""
            FOR n IN `{NODE_COLLECTION}`
                FILTER n._key == @node_id
                LIMIT 1
                RETURN n
        """

        cursor = db.aql.execute(
            query,
            bind_vars={
                "node_id": node_id
            }
        )

        list(cursor)

    else:

        key = (
            f"benchmark_"
            f"{operation_number}_"
            f"{random.randint(1, 1000000)}"
        )

        query = f"""
            INSERT {{
                _key: @key,
                benchmark: true,
                operation: @operation
            }}
            INTO `{NODE_COLLECTION}`
        """

        try:

            cursor = db.aql.execute(
                query,
                bind_vars={
                    "key": key,
                    "operation": operation_number
                }
            )

            list(cursor)

            # Delete temporary write
            delete_query = f"""
                REMOVE @key
                IN `{NODE_COLLECTION}`
            """

            cursor = db.aql.execute(
                delete_query,
                bind_vars={
                    "key": key
                }
            )

            list(cursor)

        except Exception:
            pass


# ============================================================
# MIXED WORKLOAD
# ============================================================

def run_mixed_workload(
    db,
    node_id,
    concurrency
):

    print()
    print(
        f"Concurrency: {concurrency}"
    )

    print(
        "Workload: 80% reads / 20% writes"
    )

    print(
        f"Duration: {MIXED_DURATION} seconds"
    )

    operation_counter = 0
    counter_lock = __import__("threading").Lock()

    start_time = time.perf_counter()

    def worker(worker_id):

        nonlocal operation_counter

        local_operations = 0

        while (
            time.perf_counter() - start_time
            < MIXED_DURATION
        ):

            with counter_lock:

                operation_counter += 1

                current_operation = operation_counter

            mixed_operation(
                db,
                node_id,
                current_operation
            )

            local_operations += 1

        return local_operations

    with ThreadPoolExecutor(
        max_workers=concurrency
    ) as executor:

        futures = []

        for worker_id in range(concurrency):

            futures.append(
                executor.submit(
                    worker,
                    worker_id
                )
            )

        operations = 0

        for future in futures:

            try:
                operations += future.result()

            except Exception:
                pass

    elapsed = (
        time.perf_counter()
        - start_time
    )

    throughput = (
        operations / elapsed
        if elapsed > 0
        else 0
    )

    print(
        f"Operations: {operations}"
    )

    print(
        f"Elapsed:    {elapsed:.2f} seconds"
    )

    print(
        f"Throughput: {throughput:.2f} ops/sec"
    )

    return {

        "Database": "ArangoDB",

        "Concurrency": concurrency,

        "Operations": operations,

        "Elapsed_seconds":
            round(elapsed, 2),

        "Throughput_ops_sec":
            round(throughput, 2)
    }


# ============================================================
# SAVE MIXED RESULTS
# ============================================================

def save_mixed_results(results):

    fieldnames = [

        "Database",
        "Concurrency",
        "Operations",
        "Elapsed_seconds",
        "Throughput_ops_sec"
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


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "ARANGODB GRAPH DATABASE BENCHMARK"
    )

    print("=" * 70)

    client, db = connect_arangodb()

    try:

        print()
        print(
            "Connected to ArangoDB"
        )

        # ----------------------------------------------------
        # SERVER VERSION
        # ----------------------------------------------------

        version = get_server_version(db)

        print(
            f"Server Version: {version}"
        )

        print(
            f"Python Client:  {client.version}"
        )

        # ----------------------------------------------------
        # VERIFY DATA
        # ----------------------------------------------------

        print()
        print("=" * 70)

        print(
            "VERIFYING DATA"
        )

        print("=" * 70)

        node_collection = db.collection(
            NODE_COLLECTION
        )

        edge_collection = db.collection(
            EDGE_COLLECTION
        )

        node_count = node_collection.count()
        edge_count = edge_collection.count()

        print(
            f"Nodes:         {node_count}"
        )

        print(
            f"Relationships: {edge_count}"
        )

        if node_count == 0:

            raise RuntimeError(
                "ArangoDB node collection is empty"
            )

        if edge_count == 0:

            raise RuntimeError(
                "ArangoDB edge collection is empty"
            )

        # ----------------------------------------------------
        # TEST NODE
        # ----------------------------------------------------

        test_node = find_test_node(db)

        print(
            f"Test node:     {test_node}"
        )

        bind_vars = {

            "@nodes":
                NODE_COLLECTION,

            "@edges":
                EDGE_COLLECTION,

            "node_id":
                test_node,

            "start_vertex":
                f"{NODE_COLLECTION}/{test_node}"
        }

        # ----------------------------------------------------
        # LATENCY BENCHMARK
        # ----------------------------------------------------

     # ----------------------------------------------------
# LATENCY BENCHMARK
# ----------------------------------------------------

print()
print("=" * 70)
print("LATENCY BENCHMARK")
print("=" * 70)

results = []

for query_name, query in QUERIES.items():

    if query_name in ["Node_Count", "Relationship_Count"]:
        query_bind_vars = {
            "@nodes": NODE_COLLECTION,
            "@edges": EDGE_COLLECTION
        }

    elif query_name == "Indexed_Lookup":
        query_bind_vars = {
            "@nodes": NODE_COLLECTION,
            "node_id": test_node
        }

    else:
        query_bind_vars = {
            "@edges": EDGE_COLLECTION,
            "start_vertex": f"{NODE_COLLECTION}/{test_node}"
        }

    result = benchmark_query(
        db,
        query_name,
        query,
        query_bind_vars
    )

    results.append(result)

save_latency_results(results)

        # ----------------------------------------------------
        # MIXED WORKLOAD
        # ----------------------------------------------------

        print()
        print("=" * 70)

        print(
            "MIXED READ/WRITE WORKLOAD"
        )

        print("=" * 70)

        print(
            "Workload: 80% reads / 20% writes"
        )

        print(
            f"Duration: {MIXED_DURATION} seconds"
        )

        mixed_results = []

        for concurrency in CONCURRENCY_LEVELS:

            result = run_mixed_workload(
                db,
                test_node,
                concurrency
            )

            mixed_results.append(
                result
            )

        save_mixed_results(
            mixed_results
        )

        print()
        print(
            f"Mixed workload results saved to: "
            f"{MIXED_OUTPUT}"
        )

        # ----------------------------------------------------
        # FINAL SUMMARY
        # ----------------------------------------------------

        print()
        print("=" * 70)

        print(
            "ARANGODB BENCHMARK COMPLETE"
        )

        print("=" * 70)

        print()
        print(
            "Generated files:"
        )

        print(
            f"  {LATENCY_OUTPUT}"
        )

        print(
            f"  {MIXED_OUTPUT}"
        )

        print()
        print(
            "Latency summary:"
        )

        print()

        for result in results:

            print(
                f"{result['Query']:<25}"
                f"{result['Average_ms']:>12.4f} ms"
            )

        print()
        print(
            "Mixed workload summary:"
        )

        print()

        for result in mixed_results:

            print(
                f"Concurrency {result['Concurrency']:<3}"
                f" {result['Throughput_ops_sec']:>10.2f}"
                f" ops/sec"
            )

    finally:

        client.close()


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    main()