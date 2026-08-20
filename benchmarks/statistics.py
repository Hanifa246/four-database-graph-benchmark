import statistics


def percentile(values, percentile):
    """
    Calculate percentile using linear interpolation.
    """
    if not values:
        raise ValueError("No values provided.")

    values = sorted(values)

    position = (len(values) - 1) * percentile / 100
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)

    if lower == upper:
        return values[lower]

    weight = position - lower

    return (
        values[lower]
        + weight * (values[upper] - values[lower])
    )


def calculate_statistics(values):
    return {
        "runs": len(values),
        "average_ms": statistics.mean(values),
        "min_ms": min(values),
        "max_ms": max(values),
        "p50_ms": percentile(values, 50),
        "p95_ms": percentile(values, 95),
    }