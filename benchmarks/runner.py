import time
from benchmarks.statistics import calculate_statistics
def warmup(query_function, warmup_runs=20):
    """
    Execute queries before collecting benchmark measurements.
    """
    for _ in range(warmup_runs):
        query_function()


def benchmark(
    query_function,
    runs=100,
    warmup_runs=20
):
    """
    Run a workload after warm-up and return latency statistics.
    """

    warmup(query_function, warmup_runs)

    latencies = []

    for _ in range(runs):

        start = time.perf_counter()

        query_function()

        end = time.perf_counter()

        latency_ms = (end - start) * 1000

        latencies.append(latency_ms)

    return calculate_statistics(latencies)