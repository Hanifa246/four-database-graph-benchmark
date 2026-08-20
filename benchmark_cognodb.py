import os
import csv
import time
import statistics
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")


DATASET_FILE = Path(
    "data/processed/pokec_100k_edges.csv"
)

BENCHMARK_NODES_FILE = Path(
    "data/benchmark_nodes.csv"
)

RESULTS_DIR = Path(
    "data/results"
)

RAW_RESULTS_FILE = (
    RESULTS_DIR /
    "cognodb_benchmark_raw.csv"
)

SUMMARY_FILE = (
    RESULTS_DIR /
    "cognodb_benchmark_summary.csv"
)


# ============================================================
# BENCHMARK SETTINGS
# ============================================================

ITERATIONS = 100

WARMUP_ITERATIONS = 10

EXPECTED_RELATIONSHIPS = 100_000


# ============================================================
# CYPHER QUERIES
# ============================================================

QUERIES = {

    "1-hop": """
        MATCH (p:Person {id: $id})
              -[:FRIEND]->(friend)
        RETURN count(friend) AS result
    """,

    "2-hop": """
        MATCH (p:Person {id: $id})
              -[:FRIEND*2]->(friend)
        RETURN count(DISTINCT friend) AS result
    """,

    "3-hop": """
        MATCH (p:Person {id: $id})
              -[:FRIEND*3]->(friend)
        RETURN count(DISTINCT friend) AS result
    """
}


# ============================================================
# VALIDATION
# ============================================================

if not URI:
    raise ValueError(
        "COGNODB_URI missing from .env"
    )

if not USERNAME:
    raise ValueError(
        "COGNODB_USERNAME missing from .env"
    )

if not PASSWORD:
    raise ValueError(
        "COGNODB_PASSWORD missing from .env"
    )


if not DATASET_FILE.exists():

    raise FileNotFoundError(
        f"Dataset not found:\n"
        f"{DATASET_FILE.resolve()}"
    )


if not BENCHMARK_NODES_FILE.exists():

    raise FileNotFoundError(
        f"Benchmark nodes file not found:\n"
        f"{BENCHMARK_NODES_FILE.resolve()}"
    )


# ============================================================
# RESULTS DIRECTORY
# ============================================================

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# READ BENCHMARK NODES
# ============================================================

print("=" * 70)
print("                 COGNODB GRAPH BENCHMARK")
print("=" * 70)

print()

print(
    "Benchmark nodes:"
)

print(
    BENCHMARK_NODES_FILE.resolve()
)


benchmark_nodes = []


with open(
    BENCHMARK_NODES_FILE,
    "r",
    encoding="utf-8",
    newline=""
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        benchmark_nodes.append(
            int(row["node_id"])
        )


print()

print(
    f"Benchmark starting nodes: "
    f"{len(benchmark_nodes)}"
)

for node in benchmark_nodes:

    print(
        f"  {node}"
    )


# ============================================================
# DRIVER
# ============================================================

print()

print(
    "Connecting to CognoDB..."
)

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD),
    max_connection_lifetime=300,
    connection_timeout=30
)

driver.verify_connectivity()

print(
    "✅ Connected to CognoDB"
)


# ============================================================
# DATABASE VERIFICATION
# ============================================================

print()

print(
    "Checking database..."
)

with driver.session() as session:

    node_count = session.run(
        """
        MATCH (n:Person)
        RETURN count(n) AS count
        """
    ).single()["count"]

    relationship_count = session.run(
        """
        MATCH ()-[r:FRIEND]->()
        RETURN count(r) AS count
        """
    ).single()["count"]


print(
    f"Database nodes: "
    f"{node_count:,}"
)

print(
    f"Database relationships: "
    f"{relationship_count:,}"
)


if relationship_count != EXPECTED_RELATIONSHIPS:

    driver.close()

    raise RuntimeError(
        f"Expected {EXPECTED_RELATIONSHIPS:,} "
        f"relationships but found "
        f"{relationship_count:,}."
    )


print(
    "✅ Database verification passed."
)


# ============================================================
# WARM-UP
# ============================================================

print()
print("=" * 70)
print("                         WARM-UP")
print("=" * 70)

print()

print(
    f"Running {WARMUP_ITERATIONS} warm-up "
    f"executions per query/node..."
)


for query_name, query in QUERIES.items():

    print(
        f"Warming up {query_name}..."
    )

    for node_id in benchmark_nodes:

        try:

            with driver.session() as session:

                for _ in range(
                    WARMUP_ITERATIONS
                ):

                    result = session.run(
                        query,
                        id=node_id
                    )

                    result.single()

                    result.consume()

        except ServiceUnavailable:

            print(
                "Connection reset during "
                "warm-up. Reconnecting..."
            )

            driver.close()

            driver = GraphDatabase.driver(
                URI,
                auth=(USERNAME, PASSWORD),
                max_connection_lifetime=300,
                connection_timeout=30
            )

            driver.verify_connectivity()


print()

print(
    "✅ Warm-up completed."
)


# ============================================================
# BENCHMARK
# ============================================================

print()
print("=" * 70)
print("                       BENCHMARK")
print("=" * 70)

print()

print(
    f"Starting nodes        : "
    f"{len(benchmark_nodes)}"
)

print(
    f"Iterations/query/node : "
    f"{ITERATIONS}"
)

print(
    f"Warm-up iterations    : "
    f"{WARMUP_ITERATIONS}"
)

print(
    f"Queries               : "
    f"{len(QUERIES)}"
)

expected_measurements = (
    len(benchmark_nodes)
    * ITERATIONS
    * len(QUERIES)
)

print(
    f"Expected measurements : "
    f"{expected_measurements:,}"
)


# ============================================================
# RAW RESULTS
# ============================================================

raw_results = []


# ============================================================
# EXECUTE BENCHMARK
# ============================================================

for query_name, query in QUERIES.items():

    print()

    print(
        f"Running {query_name} query..."
    )

    successful = 0

    failed = 0

    for node_id in benchmark_nodes:

        iteration = 0

        while iteration < ITERATIONS:

            try:

                with driver.session() as session:

                    start_time = (
                        time.perf_counter()
                    )

                    result = session.run(
                        query,
                        id=node_id
                    )

                    record = result.single()

                    result.consume()

                    end_time = (
                        time.perf_counter()
                    )

                elapsed_ms = (
                    end_time - start_time
                ) * 1000


                result_count = (
                    record["result"]
                    if record is not None
                    else 0
                )


                raw_results.append({

                    "query": query_name,

                    "node_id": node_id,

                    "iteration": iteration + 1,

                    "latency_ms": elapsed_ms,

                    "result_count": result_count

                })


                successful += 1

                iteration += 1


            except ServiceUnavailable:

                failed += 1

                print(
                    f"Connection reset during "
                    f"{query_name}, node "
                    f"{node_id}, iteration "
                    f"{iteration + 1}."
                )

                print(
                    "Reconnecting..."
                )


                try:

                    driver.close()

                except Exception:

                    pass


                driver = GraphDatabase.driver(
                    URI,
                    auth=(USERNAME, PASSWORD),
                    max_connection_lifetime=300,
                    connection_timeout=30
                )

                driver.verify_connectivity()

                print(
                    "✅ Reconnected."
                )


    print(
        f"Successful executions: "
        f"{successful:,}"
    )

    print(
        f"Connection retries: "
        f"{failed:,}"
    )


# ============================================================
# PERCENTILE FUNCTION
# ============================================================

def percentile(
    values,
    percentile_value
):

    values = sorted(values)

    if not values:

        return 0.0

    position = (
        (len(values) - 1)
        * percentile_value
        / 100
    )

    lower = int(position)

    upper = lower + 1

    if upper >= len(values):

        return values[lower]

    fraction = (
        position - lower
    )

    return (
        values[lower]
        +
        (
            values[upper]
            -
            values[lower]
        )
        *
        fraction
    )


# ============================================================
# SUMMARY
# ============================================================

summary = []


for query_name in QUERIES:

    values = [

        row["latency_ms"]

        for row in raw_results

        if row["query"] == query_name

    ]


    if not values:

        continue


    summary.append({

        "query": query_name,

        "measurements": len(values),

        "min_ms": min(values),

        "average_ms": statistics.mean(values),

        "p50_ms": percentile(
            values,
            50
        ),

        "p95_ms": percentile(
            values,
            95
        ),

        "max_ms": max(values)

    })


# ============================================================
# SAVE RAW RESULTS
# ============================================================

print()

print(
    "Saving raw benchmark results..."
)


with open(
    RAW_RESULTS_FILE,
    "w",
    encoding="utf-8",
    newline=""
) as file:

    fieldnames = [

        "query",

        "node_id",

        "iteration",

        "latency_ms",

        "result_count"

    ]


    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )


    writer.writeheader()

    writer.writerows(
        raw_results
    )


# ============================================================
# SAVE SUMMARY
# ============================================================

print(
    "Saving benchmark summary..."
)


with open(
    SUMMARY_FILE,
    "w",
    encoding="utf-8",
    newline=""
) as file:

    fieldnames = [

        "query",

        "measurements",

        "min_ms",

        "average_ms",

        "p50_ms",

        "p95_ms",

        "max_ms"

    ]


    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )


    writer.writeheader()

    writer.writerows(
        summary
    )


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print("=" * 70)
print("                    BENCHMARK RESULTS")
print("=" * 70)

print()

print(
    f"{'Query':<10}"
    f"{'Runs':>10}"
    f"{'Average':>15}"
    f"{'P50':>15}"
    f"{'P95':>15}"
)

print("-" * 65)


for result in summary:

    print(

        f"{result['query']:<10}"

        f"{result['measurements']:>10}"

        f"{result['average_ms']:>14.3f} ms"

        f"{result['p50_ms']:>14.3f} ms"

        f"{result['p95_ms']:>14.3f} ms"

    )


# ============================================================
# FINAL
# ============================================================

print()

print("=" * 70)
print("                    BENCHMARK COMPLETE")
print("=" * 70)

print()

print(
    "Raw results:"
)

print(
    RAW_RESULTS_FILE.resolve()
)

print()

print(
    "Summary:"
)

print(
    SUMMARY_FILE.resolve()
)

print()

print(
    f"Total successful measurements: "
    f"{len(raw_results):,}"
)

print()

print(
    "✅ Benchmark completed."
)


driver.close()