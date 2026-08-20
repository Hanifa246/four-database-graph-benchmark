import csv
from pathlib import Path

RESULTS = Path("results")

output_file = RESULTS / "four_database_comparison.csv"

files = [
    "aggregation_results.csv",
    "aggregation_memgraph_results.csv",
    "aggregation_falkordb_results.csv",

    "lookup_results.csv",
    "lookup_memgraph_results.csv",
    "lookup_falkordb_results.csv",

    "traversal_results.csv",
    "traversal_memgraph_results.csv",
    "traversal_falkordb_results.csv",

    "mixed_workload_results.csv",
    "mixed_memgraph_results.csv",
    "mixed_falkordb_results.csv"
]

rows = []

for filename in files:

    path = RESULTS / filename

    if not path.exists():
        print(f"WARNING: Missing {filename}")
        continue

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            rows.append(row)


with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    if rows:

        fieldnames = [
            "Database",
            "Workload",
            "Runs",
            "Average_ms",
            "Min_ms",
            "Max_ms",
            "P50_ms",
            "P95_ms",
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

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore"
        )

        writer.writeheader()

        for row in rows:

            for field in fieldnames:
                if field not in row:
                    row[field] = ""

            writer.writerow(row)


print("=" * 70)
print("FOUR DATABASE COMPARISON CREATED")
print("=" * 70)
print(f"Output: {output_file}")
print(f"Rows:   {len(rows)}")