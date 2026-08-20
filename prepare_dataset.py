from pathlib import Path
import gzip
import random

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path(
    "data/raw/soc-pokec-relationships.txt.gz"
)

OUTPUT_DIR = Path("data/processed")

OUTPUT_FILE = OUTPUT_DIR / "pokec_100k_edges.csv"

TARGET_RELATIONSHIPS = 100_000

# Fixed seed makes the dataset reproducible
RANDOM_SEED = 42


# ============================================================
# CHECK INPUT
# ============================================================

if not INPUT_FILE.exists():

    print("❌ Dataset file not found:")
    print(INPUT_FILE.resolve())

    raise SystemExit(1)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# RESERVOIR SAMPLING
# ============================================================

print("=" * 60)
print("      SNAP Pokec Benchmark Dataset Preparation")
print("=" * 60)

print()
print("Input:")
print(INPUT_FILE.resolve())

print()
print("Target relationships:", TARGET_RELATIONSHIPS)
print("Random seed:", RANDOM_SEED)

print()
print("Reading original dataset...")

random.seed(RANDOM_SEED)

sample = []

total_relationships = 0


with gzip.open(
    INPUT_FILE,
    "rt",
    encoding="utf-8"
) as file:

    for line in file:

        line = line.strip()

        # Ignore empty lines
        if not line:
            continue

        # Ignore comments
        if line.startswith("#"):
            continue

        parts = line.split()

        if len(parts) < 2:
            continue

        try:

            source = int(parts[0])
            target = int(parts[1])

        except ValueError:

            continue

        total_relationships += 1

        # ----------------------------------------------------
        # Reservoir sampling
        # ----------------------------------------------------

        if len(sample) < TARGET_RELATIONSHIPS:

            sample.append(
                (source, target)
            )

        else:

            index = random.randint(
                0,
                total_relationships - 1
            )

            if index < TARGET_RELATIONSHIPS:

                sample[index] = (
                    source,
                    target
                )


# ============================================================
# DISPLAY ORIGINAL DATASET SIZE
# ============================================================

print()
print(
    f"Original relationships found: "
    f"{total_relationships:,}"
)

print(
    f"Sampled relationships: "
    f"{len(sample):,}"
)


# ============================================================
# FIND UNIQUE NODES
# ============================================================

nodes = set()

for source, target in sample:

    nodes.add(source)
    nodes.add(target)


# ============================================================
# WRITE CSV
# ============================================================

print()
print("Creating benchmark CSV...")

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8",
    newline=""
) as file:

    file.write("source,target\n")

    for source, target in sample:

        file.write(
            f"{source},{target}\n"
        )


# ============================================================
# FINAL VERIFICATION
# ============================================================

relationship_count = len(sample)

node_count = len(nodes)


print()
print("=" * 60)
print("             BENCHMARK DATASET")
print("=" * 60)

print()
print(
    f"Nodes         : {node_count:,}"
)

print(
    f"Relationships : {relationship_count:,}"
)

print()
print("Output file:")
print(OUTPUT_FILE.resolve())


# ============================================================
# VALIDATION
# ============================================================

print()

if relationship_count == 100_000:

    print(
        "✅ EXACTLY 100,000 relationships created."
    )

else:

    print(
        "❌ ERROR: Relationship count is not 100,000."
    )

    raise SystemExit(1)


print()
print("=" * 60)
print("                 SUCCESS")
print("=" * 60)

print()
print("This CSV will be the identical benchmark")
print("dataset loaded into all five databases.")