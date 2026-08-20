from pathlib import Path
import csv

FILE = Path("data/processed/pokec_100k_edges.csv")

EXPECTED_RELATIONSHIPS = 100_000

print("=" * 60)
print("           BENCHMARK DATASET VERIFICATION")
print("=" * 60)

print()
print("File:")
print(FILE.resolve())

if not FILE.exists():
    print("❌ CSV file not found!")
    raise SystemExit(1)

nodes = set()
relationships = 0
duplicates = 0
seen_relationships = set()

with open(FILE, "r", encoding="utf-8") as f:

    reader = csv.DictReader(f)

    if reader.fieldnames != ["source", "target"]:
        print("❌ Invalid CSV columns:")
        print(reader.fieldnames)
        raise SystemExit(1)

    for row in reader:

        source = int(row["source"])
        target = int(row["target"])

        relationship = (source, target)

        if relationship in seen_relationships:
            duplicates += 1
        else:
            seen_relationships.add(relationship)

        nodes.add(source)
        nodes.add(target)

        relationships += 1

print()
print("Nodes:", f"{len(nodes):,}")
print("Relationships:", f"{relationships:,}")
print("Duplicate relationships:", f"{duplicates:,}")

print()

if relationships == EXPECTED_RELATIONSHIPS:
    print("✅ Relationship count is correct.")
else:
    print("❌ Relationship count is incorrect.")
    raise SystemExit(1)

print()
print("=" * 60)
print("             DATASET VERIFICATION PASSED")
print("=" * 60)