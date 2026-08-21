from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)
from pathlib import Path


# ============================================================
# FILE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = RESULTS_DIR / "Five_Database_Graph_Benchmark_Report.pdf"

PERFORMANCE_GRAPH = RESULTS_DIR / "four_database_performance.png"
SPEEDUP_GRAPH = RESULTS_DIR / "four_database_speedup.png"
MIXED_GRAPH = RESULTS_DIR / "four_database_mixed_workload.png"

# Optional five-database graphs
FIVE_PERFORMANCE_GRAPH = RESULTS_DIR / "five_database_performance.png"
FIVE_MIXED_GRAPH = RESULTS_DIR / "five_database_mixed_workload.png"
FIVE_SPEEDUP_GRAPH = RESULTS_DIR / "five_database_speedup.png"


# ============================================================
# DOCUMENT SETUP
# ============================================================

doc = SimpleDocTemplate(
    str(OUTPUT_FILE),
    pagesize=A4,
    rightMargin=42,
    leftMargin=42,
    topMargin=45,
    bottomMargin=45,
)


# ============================================================
# STYLES
# ============================================================

styles = getSampleStyleSheet()

styles.add(
    ParagraphStyle(
        name="TitleCenter",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        leading=27,
        spaceAfter=12,
    )
)

styles.add(
    ParagraphStyle(
        name="SubtitleCenter",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=11,
        leading=16,
        spaceAfter=18,
    )
)

styles.add(
    ParagraphStyle(
        name="Section",
        parent=styles["Heading1"],
        fontSize=15,
        leading=19,
        spaceBefore=14,
        spaceAfter=9,
        textColor=colors.HexColor("#17365D"),
    )
)

styles.add(
    ParagraphStyle(
        name="SubSection",
        parent=styles["Heading2"],
        fontSize=11.5,
        leading=15,
        spaceBefore=9,
        spaceAfter=6,
        textColor=colors.HexColor("#244062"),
    )
)

styles.add(
    ParagraphStyle(
        name="Body2",
        parent=styles["BodyText"],
        fontSize=9.3,
        leading=14,
        spaceAfter=7,
    )
)

styles.add(
    ParagraphStyle(
        name="Small",
        parent=styles["BodyText"],
        fontSize=7.8,
        leading=10.5,
    )
)

styles.add(
    ParagraphStyle(
        name="FigureCaption",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=8,
        leading=11,
        spaceBefore=4,
        spaceAfter=10,
    )
)

styles.add(
    ParagraphStyle(
        name="Bullet2",
        parent=styles["BodyText"],
        fontSize=9.2,
        leading=13.5,
        leftIndent=14,
        firstLineIndent=-8,
        spaceAfter=5,
    )
)


story = []


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def add_bullet(text):
    story.append(
        Paragraph(
            "• " + text,
            styles["Bullet2"],
        )
    )


def add_table(data, widths, font_size=8.2):
    table = Table(
        data,
        colWidths=widths,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#D9EAF7"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "Helvetica",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    font_size,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F7F9FC"),
                    ],
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 8))


def add_figure(path, caption, width=6.25, height=3.8):
    if path.exists():
        story.append(
            Image(
                str(path),
                width=width * inch,
                height=height * inch,
            )
        )

        story.append(
            Paragraph(
                caption,
                styles["FigureCaption"],
            )
        )
    else:
        story.append(
            Paragraph(
                f"{caption} — graph file not found.",
                styles["Small"],
            )
        )


# ============================================================
# TITLE PAGE
# ============================================================

story.append(Spacer(1, 0.35 * inch))

story.append(
    Paragraph(
        "Five-Database Graph Benchmark",
        styles["TitleCenter"],
    )
)

story.append(
    Paragraph(
        "A Reproducible Performance Evaluation of "
        "CognoDB, Neo4j Aura, Memgraph, FalkorDB, and ArangoDB",
        styles["SubtitleCenter"],
    )
)

story.append(Spacer(1, 0.12 * inch))

title_table = [
    ["Project", "Graph Database Performance Benchmark"],
    [
        "Databases",
        "CognoDB, Neo4j Aura, Memgraph, FalkorDB, ArangoDB",
    ],
    [
        "Dataset",
        "Pokec-derived graph dataset",
    ],
    [
        "Dataset size",
        "169,870 nodes and 100,000 relationships",
    ],
    [
        "Latency benchmark",
        "100 measured runs with warm-up runs",
    ],
    [
        "Mixed workload",
        "80% reads / 20% writes",
    ],
    [
        "Concurrency",
        "1, 10, and 40 clients/workers",
    ],
    [
        "ArangoDB deployment",
        "Local Docker container",
    ],
    [
        "Report",
        "Benchmark methodology, results, analysis and reproducibility",
    ],
]

add_table(
    title_table,
    [1.55 * inch, 4.45 * inch],
    font_size=8.7,
)

story.append(Spacer(1, 0.2 * inch))

story.append(
    Paragraph(
        "<b>Purpose of this report:</b> "
        "This document provides a complete technical description of the "
        "graph database benchmarking project, including database setup, "
        "dataset preparation, benchmark implementation, workload design, "
        "measurement methodology, results, analysis, fairness considerations, "
        "limitations, and reproducibility instructions.",
        styles["Body2"],
    )
)

story.append(PageBreak())


# ============================================================
# 1. EXECUTIVE SUMMARY
# ============================================================

story.append(
    Paragraph(
        "1. Executive Summary",
        styles["Section"],
    )
)

story.append(
    Paragraph(
        "This project evaluates five graph database systems using a common "
        "Pokec-derived graph dataset and a scripted benchmark framework. "
        "The evaluated systems are CognoDB, Neo4j Aura, Memgraph, FalkorDB, "
        "and ArangoDB.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "The benchmark measures both individual query latency and concurrent "
        "mixed read/write throughput. The latency suite contains node-count "
        "aggregation, indexed point lookup, and 1-hop, 2-hop, and 3-hop "
        "graph traversal workloads. The mixed workload contains 80% reads "
        "and 20% writes and is evaluated at concurrency levels of 1, 10, "
        "and 40.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "For the four initially compared systems, FalkorDB recorded the "
        "lowest measured latency across the five latency workloads and the "
        "highest measured mixed-workload throughput. ArangoDB was subsequently "
        "added as the fifth database and successfully loaded with the same "
        "169,870-node and 100,000-edge dataset. Its benchmark produced "
        "independent latency and concurrency measurements.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "The results are benchmark-specific. They should not be interpreted "
        "as universal rankings because database architecture, cloud tier, "
        "deployment topology, hardware, network conditions, indexing, query "
        "language, configuration, and client overhead can affect measured "
        "performance.",
        styles["Body2"],
    )
)


# ============================================================
# 2. PROJECT OBJECTIVES
# ============================================================

story.append(
    Paragraph(
        "2. Project Objectives",
        styles["Section"],
    )
)

objectives = [
    "Build a reusable graph database benchmarking framework.",
    "Prepare one common graph dataset for all evaluated platforms.",
    "Implement database-specific connectors for reliable connectivity.",
    "Load the graph dataset into each benchmark platform.",
    "Measure aggregation and lookup latency.",
    "Measure 1-hop, 2-hop, and 3-hop graph traversal latency.",
    "Measure mixed read/write throughput.",
    "Evaluate concurrency at 1, 10, and 40 workers.",
    "Use warm-up and repeated runs to reduce transient effects.",
    "Save raw benchmark results as CSV files.",
    "Generate comparison tables and charts.",
    "Calculate relative performance and speedup.",
    "Document methodology, fairness, limitations and reproducibility.",
    "Prepare a GitHub-ready project and final technical report.",
]

for item in objectives:
    add_bullet(item)


# ============================================================
# 3. DATABASES EVALUATED
# ============================================================

story.append(
    Paragraph(
        "3. Databases Evaluated",
        styles["Section"],
    )
)

database_data = [
    ["Database", "Role in Project", "Benchmark Status"],
    [
        "CognoDB",
        "Primary comparison platform",
        "Benchmarked",
    ],
    [
        "Neo4j Aura",
        "Managed graph database comparison",
        "Benchmarked",
    ],
    [
        "Memgraph",
        "Graph database comparison",
        "Benchmarked",
    ],
    [
        "FalkorDB",
        "Graph database comparison",
        "Benchmarked",
    ],
    [
        "ArangoDB",
        "Fifth database added for assignment completeness",
        "Loaded and benchmarked",
    ],
]

add_table(
    database_data,
    [1.25 * inch, 3.25 * inch, 1.5 * inch],
    font_size=8.2,
)

story.append(
    Paragraph(
        "<b>Important:</b> ArangoDB was added after the original "
        "four-database comparison. It is therefore documented separately "
        "in the benchmark results where the earlier four-database result "
        "files do not yet contain ArangoDB.",
        styles["Body2"],
    )
)


# ============================================================
# 4. DATASET
# ============================================================

story.append(
    Paragraph(
        "4. Dataset Preparation",
        styles["Section"],
    )
)

story.append(
    Paragraph(
        "The benchmark uses a processed Pokec-derived graph dataset. "
        "The final benchmark input is stored as a CSV file containing "
        "source and target identifiers for graph relationships.",
        styles["Body2"],
    )
)

dataset_data = [
    ["Property", "Value"],
    ["Dataset", "Pokec-derived processed dataset"],
    ["Input file", "data/processed/pokec_100k_edges.csv"],
    ["Columns", "source, target"],
    ["Relationships", "100,000"],
    ["Unique nodes", "169,870"],
    ["Graph type", "Directed relationship dataset"],
]

add_table(
    dataset_data,
    [2.0 * inch, 4.0 * inch],
)

story.append(
    Paragraph(
        "The dataset was explicitly verified before loading into ArangoDB. "
        "The validation confirmed that the CSV contained exactly 100,000 "
        "rows and the expected source/target columns.",
        styles["Body2"],
    )
)


# ============================================================
# 5. DATA LOADING AND DATABASE SETUP
# ============================================================

story.append(
    Paragraph(
        "5. Data Loading and Database Setup",
        styles["Section"],
    )
)

story.append(
    Paragraph(
        "A database-specific loader was implemented for ArangoDB. The loader "
        "connects using environment variables rather than storing credentials "
        "in source code. The graph is represented using a vertex collection "
        "named <b>nodes</b> and an edge collection named "
        "<b>relationships</b>.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "The loader also creates an ArangoDB graph named "
        "<b>pokec_graph</b>. During development, a collection-deletion "
        "error occurred because the relationships collection was still part "
        "of the graph. The cleanup logic was corrected to delete the graph "
        "before deleting its collections.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "After the correction, the loader successfully performed the complete "
        "cycle of cleaning old data, creating collections, inserting nodes, "
        "inserting relationships, creating the graph, and verifying the final "
        "counts.",
        styles["Body2"],
    )
)

arangodb_setup = [
    ["ArangoDB Component", "Implemented Configuration"],
    ["Host", "http://localhost:8529"],
    ["Database", "_system"],
    ["Graph", "pokec_graph"],
    ["Node collection", "nodes"],
    ["Edge collection", "relationships"],
    ["Nodes loaded", "169,870"],
    ["Relationships loaded", "100,000"],
    ["Deployment", "Docker"],
]

add_table(
    arangodb_setup,
    [2.0 * inch, 4.0 * inch],
)


# ============================================================
# 6. CONNECTION AND SECURITY
# ============================================================

story.append(
    Paragraph(
        "6. Database Connectivity and Credential Handling",
        styles["Section"],
    )
)

story.append(
    Paragraph(
        "Database credentials are not embedded directly in benchmark source "
        "code. The project uses environment variables loaded through "
        "<b>python-dotenv</b>. This approach allows the same benchmark code "
        "to be reused with different credentials and prevents passwords and "
        "connection details from being committed to the repository.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "The ArangoDB connector was independently tested before the dataset "
        "loading stage. The connection test successfully reported the "
        "ArangoDB server version and confirmed a working database connection.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "<b>Repository security rule:</b> passwords, API keys, private "
        "connection URIs, and other secrets must not be committed to GitHub. "
        "A .env.example file can be provided containing variable names and "
        "placeholder values.",
        styles["Body2"],
    )
)


# ============================================================
# 7. BENCHMARK METHODOLOGY
# ============================================================

story.append(
    Paragraph(
        "7. Benchmark Methodology",
        styles["Section"],
    )
)

story.append(
    Paragraph(
        "The benchmark was designed around the principle that every database "
        "should receive the same logical workload and dataset. Query syntax "
        "is database-specific, but the intended operation is kept equivalent "
        "across systems.",
        styles["Body2"],
    )
)

methodology_data = [
    ["Methodology Item", "Configuration"],
    ["Dataset", "Same Pokec-derived graph dataset"],
    ["Latency warm-up", "Warm-up executions before measurement"],
    ["Measured latency runs", "100 runs per workload"],
    ["Latency metrics", "Average, minimum, maximum, median and P95"],
    ["Mixed workload", "80% reads / 20% writes"],
    ["Mixed workload duration", "Approximately 30 seconds"],
    ["Concurrency levels", "1, 10, 40"],
    ["Output", "CSV result files"],
    ["Visualization", "PNG comparison charts"],
]

add_table(
    methodology_data,
    [2.3 * inch, 3.7 * inch],
)


# ============================================================
# 8. WORKLOAD DEFINITIONS
# ============================================================

story.append(
    Paragraph(
        "8. Benchmark Workloads",
        styles["Section"],
    )
)

workloads = [
    (
        "Node Count",
        "Counts the number of nodes in the graph. "
        "This represents an aggregation-style workload.",
    ),
    (
        "Relationship Count",
        "Counts graph relationships. "
        "For ArangoDB this is measured using the relationships edge collection.",
    ),
    (
        "Indexed / Point Lookup",
        "Retrieves a specific node using an identifier lookup. "
        "The exact implementation is database-specific while the logical "
        "operation remains a point lookup.",
    ),
    (
        "1-Hop Traversal",
        "Traverses one relationship level from a selected starting node.",
    ),
    (
        "2-Hop Traversal",
        "Traverses exactly two relationship levels from the starting node.",
    ),
    (
        "3-Hop Traversal",
        "Traverses exactly three relationship levels from the starting node.",
    ),
    (
        "Mixed Read/Write",
        "Runs a concurrent workload consisting of approximately 80% reads "
        "and 20% writes.",
    ),
]

workload_data = [
    ["Workload", "Purpose"],
]

for name, description in workloads:
    workload_data.append([name, description])

add_table(
    workload_data,
    [1.65 * inch, 4.35 * inch],
    font_size=8.1,
)


# ============================================================
# 9. BENCHMARK IMPLEMENTATION
# ============================================================

story.append(
    Paragraph(
        "9. Benchmark Implementation",
        styles["Section"],
    )
)

story.append(
    Paragraph(
        "The benchmark implementation is written in Python. The framework "
        "contains connection handling, query definitions, warm-up execution, "
        "timing, statistical calculations, CSV generation, and concurrency "
        "testing.",
        styles["Body2"],
    )
)

implementation_items = [
    "<b>Environment loading:</b> python-dotenv is used to read database credentials.",
    "<b>Database connectivity:</b> database-specific connectors establish authenticated sessions.",
    "<b>Timing:</b> time.perf_counter() is used for high-resolution elapsed-time measurement.",
    "<b>Warm-up:</b> initial executions are performed before measured runs.",
    "<b>Repeated measurements:</b> each latency workload is executed repeatedly.",
    "<b>Statistics:</b> average, minimum, maximum, median and P95 are calculated.",
    "<b>CSV output:</b> benchmark results are stored in the results directory.",
    "<b>Concurrency:</b> mixed workloads use multiple workers to simulate concurrent clients.",
    "<b>Visualization:</b> result CSV files are used to generate comparison charts.",
]

for item in implementation_items:
    add_bullet(item)


# ============================================================
# 10. ARANGODB IMPLEMENTATION
# ============================================================

story.append(
    Paragraph(
        "10. ArangoDB Implementation",
        styles["Section"],
    )
)

story.append(
    Paragraph(
        "ArangoDB was implemented as the fifth graph database in the project. "
        "The database was deployed locally using Docker and exposed on port "
        "8529. The Python benchmark uses the python-arango client library.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "The implementation includes a connector, dataset loader, graph "
        "creation logic, data verification, latency benchmark, and mixed "
        "read/write workload benchmark.",
        styles["Body2"],
    )
)

# IMPORTANT:
# This closing parenthesis fixes the SyntaxError from your original code.
story.append(
    Paragraph(
        "The loader verified the final database contents as "
        "<b>169,870 nodes</b> and <b>100,000 relationships</b>. "
        "The ArangoDB benchmark then measured six latency workloads and "
        "three concurrency levels.",
        styles["Body2"],
    )
)


# ============================================================
# 11. ARANGODB RESULTS
# ============================================================

story.append(
    Paragraph(
        "11. ArangoDB Benchmark Results",
        styles["Section"],
    )
)

arangodb_latency = [
    [
        "Workload",
        "Average ms",
        "Minimum ms",
        "Maximum ms",
        "Median ms",
        "P95 ms",
    ],
    [
        "Node Count",
        "64.5845",
        "58.8156",
        "85.6189",
        "63.3397",
        "72.9163",
    ],
    [
        "Relationship Count",
        "54.2713",
        "51.0057",
        "60.7268",
        "53.9590",
        "58.6215",
    ],
    [
        "Indexed Lookup",
        "3.0577",
        "1.9311",
        "5.3244",
        "2.8945",
        "4.5414",
    ],
    [
        "1-Hop",
        "46.7648",
        "43.2507",
        "49.0612",
        "47.4670",
        "48.7620",
    ],
    [
        "2-Hop",
        "46.3274",
        "43.0116",
        "51.8651",
        "47.0127",
        "48.7773",
    ],
    [
        "3-Hop",
        "46.4933",
        "43.0550",
        "63.9874",
        "46.7905",
        "48.6026",
    ],
]

add_table(
    arangodb_latency,
    [
        1.35 * inch,
        0.95 * inch,
        0.95 * inch,
        0.95 * inch,
        0.95 * inch,
        0.95 * inch,
    ],
    font_size=7.2,
)

story.append(
    Paragraph(
        "The ArangoDB results show very low point-lookup latency relative to "
        "its aggregation and traversal workloads. Its indexed lookup measured "
        "approximately 3.06 ms on average. The 1-hop, 2-hop and 3-hop "
        "traversals remained close to 46–47 ms in this particular test.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "<b>Important:</b> ArangoDB results should be compared with the other "
        "databases only after confirming that query semantics, indexing, "
        "deployment resources, warm-up configuration and client-side timing "
        "are equivalent.",
        styles["Body2"],
    )
)


# ============================================================
# 12. ARANGODB MIXED WORKLOAD
# ============================================================

story.append(
    Paragraph(
        "12. ArangoDB Mixed Read/Write Results",
        styles["Section"],
    )
)

arangodb_mixed = [
    [
        "Concurrency",
        "Operations",
        "Elapsed sec",
        "Throughput ops/sec",
    ],
    ["1", "804", "30.02", "26.78"],
    ["10", "7701", "30.04", "256.36"],
    ["40", "17814", "30.06", "592.68"],
]

add_table(
    arangodb_mixed,
    [
        1.3 * inch,
        1.45 * inch,
        1.45 * inch,
        1.8 * inch,
    ],
)

story.append(
    Paragraph(
        "ArangoDB throughput increased substantially as concurrency increased. "
        "The measured throughput rose from 26.78 operations per second at "
        "concurrency 1 to 256.36 operations per second at concurrency 10 and "
        "592.68 operations per second at concurrency 40.",
        styles["Body2"],
    )
)


# ============================================================
# 13. FOUR DATABASE LATENCY RESULTS
# ============================================================

story.append(
    Paragraph(
        "13. Four-Database Latency Results",
        styles["Section"],
    )
)

four_latency = [
    [
        "Workload",
        "FalkorDB",
        "Neo4j Aura",
        "Memgraph",
        "CognoDB",
    ],
    [
        "Node Count",
        "1.41 ms",
        "91.21 ms",
        "198.75 ms",
        "318.71 ms",
    ],
    [
        "Point Lookup",
        "1.84 ms",
        "76.75 ms",
        "165.71 ms",
        "308.79 ms",
    ],
    [
        "1-Hop",
        "4.56 ms",
        "77.69 ms",
        "174.79 ms",
        "324.82 ms",
    ],
    [
        "2-Hop",
        "7.81 ms",
        "77.55 ms",
        "170.81 ms",
        "320.95 ms",
    ],
    [
        "3-Hop",
        "33.52 ms",
        "78.06 ms",
        "178.80 ms",
        "315.52 ms",
    ],
]

add_table(
    four_latency,
    [
        1.25 * inch,
        1.2 * inch,
        1.2 * inch,
        1.2 * inch,
        1.2 * inch,
    ],
)

story.append(
    Paragraph(
        "Within the original four-database comparison, FalkorDB recorded "
        "the lowest average latency for all five workloads. Neo4j Aura "
        "consistently followed FalkorDB, while Memgraph and CognoDB recorded "
        "higher measured latency in this benchmark configuration.",
        styles["Body2"],
    )
)

add_figure(
    FIVE_PERFORMANCE_GRAPH
    if FIVE_PERFORMANCE_GRAPH.exists()
    else PERFORMANCE_GRAPH,
    "Figure 1. Graph database latency comparison.",
)


# ============================================================
# 14. FOUR DATABASE MIXED WORKLOAD
# ============================================================

story.append(
    Paragraph(
        "14. Four-Database Mixed Workload Results",
        styles["Section"],
    )
)

four_mixed = [
    [
        "Concurrency",
        "FalkorDB",
        "Neo4j Aura",
        "Memgraph",
        "CognoDB",
    ],
    [
        "1",
        "491.63",
        "10.31",
        "6.00",
        "3.11",
    ],
    [
        "10",
        "1542.55",
        "119.48",
        "58.08",
        "22.13",
    ],
    [
        "40",
        "1494.16",
        "453.23",
        "230.27",
        "15.07",
    ],
]

add_table(
    four_mixed,
    [
        1.15 * inch,
        1.2 * inch,
        1.2 * inch,
        1.2 * inch,
        1.2 * inch,
    ],
)

story.append(
    Paragraph(
        "FalkorDB recorded the highest measured throughput at each tested "
        "concurrency level in the original four-database comparison. "
        "Neo4j Aura also showed a strong increase in throughput as concurrency "
        "increased, particularly between 10 and 40 workers.",
        styles["Body2"],
    )
)

add_figure(
    FIVE_MIXED_GRAPH
    if FIVE_MIXED_GRAPH.exists()
    else MIXED_GRAPH,
    "Figure 2. Mixed read/write workload throughput comparison.",
)


# ============================================================
# 15. SPEEDUP ANALYSIS
# ============================================================

story.append(
    Paragraph(
        "15. Relative Speedup Analysis",
        styles["Section"],
    )
)

speedup_data = [
    [
        "Workload",
        "Neo4j Aura",
        "Memgraph",
        "FalkorDB",
    ],
    [
        "Node Count",
        "3.49×",
        "1.60×",
        "225.76×",
    ],
    [
        "Indexed Lookup",
        "4.02×",
        "1.86×",
        "167.60×",
    ],
    [
        "1-Hop",
        "4.18×",
        "1.86×",
        "71.24×",
    ],
    [
        "2-Hop",
        "4.14×",
        "1.88×",
        "41.09×",
    ],
    [
        "3-Hop",
        "4.04×",
        "1.76×",
        "9.41×",
    ],
]

add_table(
    speedup_data,
    [
        1.7 * inch,
        1.35 * inch,
        1.35 * inch,
        1.35 * inch,
    ],
)

story.append(
    Paragraph(
        "The speedup figures describe how much lower the measured latency "
        "was relative to CognoDB for the original four-database experiment. "
        "For example, a 225.76× figure means the measured CognoDB average "
        "latency was approximately 225.76 times the FalkorDB average for "
        "that workload.",
        styles["Body2"],
    )
)

add_figure(
    FIVE_SPEEDUP_GRAPH
    if FIVE_SPEEDUP_GRAPH.exists()
    else SPEEDUP_GRAPH,
    "Figure 3. Relative latency speedup compared with CognoDB.",
)


# ============================================================
# 16. ANALYSIS
# ============================================================

story.append(
    Paragraph(
        "16. Analysis and Interpretation",
        styles["Section"],
    )
)

analysis_items = [
    "FalkorDB produced the lowest measured latency across all five latency workloads in the original four-database comparison.",
    "The largest latency advantage occurred in node-count aggregation, where FalkorDB averaged approximately 1.41 ms compared with approximately 318.71 ms for CognoDB.",
    "FalkorDB also showed very low point-lookup latency at approximately 1.84 ms.",
    "As traversal depth increased from one hop to three hops, FalkorDB latency increased, showing that deeper traversal was more expensive even for the fastest system.",
    "Neo4j Aura maintained a relatively stable latency profile across the traversal workloads.",
    "Memgraph and CognoDB showed higher latency under the tested workload and configuration.",
    "In the mixed workload, FalkorDB achieved the highest throughput among the original four systems at all three concurrency levels.",
    "ArangoDB showed strong scaling within its own benchmark: throughput increased from 26.78 ops/sec at concurrency 1 to 592.68 ops/sec at concurrency 40.",
    "The ArangoDB result demonstrates why the fifth database must be included in the final comparison matrix rather than leaving the project as a four-database benchmark.",
]

for item in analysis_items:
    add_bullet(item)

story.append(
    Paragraph(
        "<b>Root-cause interpretation:</b> differences between graph databases "
        "can arise from their internal storage engines, indexing structures, "
        "query planners, traversal execution strategies, caching, concurrency "
        "models, network overhead, deployment architecture, and resource "
        "allocation. The benchmark identifies measured differences but does "
        "not by itself prove a single architectural cause for every difference.",
        styles["Body2"],
    )
)


# ============================================================
# 17. METHODOLOGY & FAIRNESS
# ============================================================

story.append(
    Paragraph(
        "17. Methodology and Fairness",
        styles["Section"],
    )
)

story.append(
    Paragraph(
        "Methodology and fairness represent a major evaluation criterion "
        "because benchmark results are meaningful only when the comparison "
        "is performed consistently.",
        styles["Body2"],
    )
)

fairness_data = [
    ["Fairness Requirement", "How It Is Addressed"],
    [
        "Same data",
        "The benchmark is based on the same processed Pokec-derived graph dataset.",
    ],
    [
        "Same logical workloads",
        "Aggregation, point lookup and traversal workloads are defined consistently.",
    ],
    [
        "Warm-up",
        "Warm-up executions are performed before measured latency runs.",
    ],
    [
        "Repeated runs",
        "Latency is measured over repeated executions and summarized statistically.",
    ],
    [
        "Concurrency sweep",
        "Mixed workload is tested at concurrency 1, 10 and 40.",
    ],
    [
        "Credential isolation",
        "Credentials are read from environment variables rather than source code.",
    ],
    [
        "Caveats",
        "Deployment and resource differences are explicitly acknowledged.",
    ],
]

add_table(
    fairness_data,
    [1.8 * inch, 4.2 * inch],
    font_size=7.9,
)

story.append(
    Paragraph(
        "<b>Fairness caveat:</b> a completely identical hardware and network "
        "environment may not be possible when comparing managed cloud services "
        "with locally hosted databases. The final README should therefore "
        "document each platform's deployment type, resource limits, region "
        "where relevant, and any free-tier restrictions.",
        styles["Body2"],
    )
)


# ============================================================
# 18. REPRODUCIBILITY
# ============================================================

story.append(
    Paragraph(
        "18. Reproducibility and Code Quality",
        styles["Section"],
    )
)

story.append(
    Paragraph(
        "The project is structured so that database setup, loading, benchmarking "
        "and result generation are performed through scripts rather than manual "
        "query execution. This makes the experiment easier to repeat and audit.",
        styles["Body2"],
    )
)

repro_items = [
    "Python virtual environment is used for project dependencies.",
    "Database-specific connector scripts validate connectivity.",
    "Dataset loading is scripted.",
    "ArangoDB deployment is reproducible using Docker.",
    "Benchmark execution is scripted.",
    "Latency results are automatically written to CSV.",
    "Mixed workload results are automatically written to CSV.",
    "Comparison scripts generate summary files and visualizations.",
    "Environment variables are used for credentials.",
    "The README should document installation, environment variables and execution commands.",
    "Dependencies should be pinned in requirements.txt before final submission.",
]

for item in repro_items:
    add_bullet(item)

story.append(
    Paragraph(
        "<b>Recommended final one-command workflow:</b> "
        "after dependencies and database credentials are configured, the "
        "repository should provide a single documented command or script "
        "that runs the required benchmark sequence and writes the results "
        "into the results/ directory.",
        styles["Body2"],
    )
)


# ============================================================
# 19. RESULTS ARTIFACTS
# ============================================================

story.append(
    Paragraph(
        "19. Generated Results and Artifacts",
        styles["Section"],
    )
)

artifact_data = [
    ["Artifact", "Purpose"],
    [
        "Benchmark Python scripts",
        "Execute latency and mixed-workload benchmarks.",
    ],
    [
        "Database connectors",
        "Connect to each graph database.",
    ],
    [
        "Dataset loaders",
        "Load the common graph dataset.",
    ],
    [
        "Latency CSV files",
        "Store repeated-run measurements.",
    ],
    [
        "Mixed workload CSV files",
        "Store concurrency throughput results.",
    ],
    [
        "Comparison CSV files",
        "Combine database results for analysis.",
    ],
    [
        "Performance PNG",
        "Visualize latency comparisons.",
    ],
    [
        "Speedup PNG",
        "Visualize relative performance.",
    ],
    [
        "Mixed workload PNG",
        "Visualize throughput versus concurrency.",
    ],
    [
        "Final PDF report",
        "Present methodology, results and analysis.",
    ],
]

add_table(
    artifact_data,
    [2.0 * inch, 4.0 * inch],
    font_size=8,
)


# ============================================================
# 20. REPOSITORY STRUCTURE
# ============================================================

story.append(
    Paragraph(
        "20. Recommended GitHub Repository Structure",
        styles["Section"],
    )
)

repo_structure = [
    "data/",
    "  processed/",
    "    pokec_100k_edges.csv",
    "connectors/",
    "  arangodb.py",
    "  cognodb.py",
    "  neo4j.py",
    "  memgraph.py",
    "  falkordb.py",
    "results/",
    "  benchmark CSV files",
    "  comparison CSV files",
    "  PNG charts",
    "benchmarks/",
    "  database benchmark scripts",
    "load_arangodb.py",
    "benchmark_arangodb.py",
    "create_comparison.py",
    "plot_comparison_log.py",
    "requirements.txt",
    ".env.example",
    ".gitignore",
    "README.md",
]

story.append(
    Paragraph(
        "<br/>".join(repo_structure),
        styles["Small"],
    )
)


# ============================================================
# 21. ASSIGNMENT REQUIREMENTS
# ============================================================

story.append(
    Paragraph(
        "21. Assignment Requirement Coverage",
        styles["Section"],
    )
)

assignment_data = [
    ["Evaluation Criterion", "Project Coverage"],
    [
        "Methodology & fairness — 25%",
        "Common dataset, logical workload definitions, warm-up, repeated runs, concurrency sweep and explicit caveats.",
    ],
    [
        "Completeness of metrics — 20%",
        "Latency and mixed read/write workloads are implemented. Final five-database matrix should include all required metrics for every platform.",
    ],
    [
        "Reproducibility & code quality — 20%",
        "Scripted loaders, connectors, benchmark runners, CSV outputs and environment-based credentials.",
    ],
    [
        "README & analysis — 15%",
        "README should contain methodology, environment specifications, dataset details, results matrix, charts, analysis and caveats.",
    ],
    [
        "Communication — 20%",
        "This report provides a structured explanation of the project, implementation, methodology, results, interpretation and limitations.",
    ],
]

add_table(
    assignment_data,
    [2.15 * inch, 3.85 * inch],
    font_size=7.8,
)

story.append(
    Paragraph(
        "<b>Final status:</b> the core technical benchmark implementation is "
        "substantially complete. Before submission, the remaining important "
        "work is to consolidate ArangoDB into the same five-database results "
        "matrix, verify that every required metric is available for all five "
        "platforms, pin dependencies, finalize the README, and ensure that "
        "no credentials or private connection strings are committed.",
        styles["Body2"],
    )
)


# ============================================================
# 22. LIMITATIONS
# ============================================================

story.append(
    Paragraph(
        "22. Limitations and Caveats",
        styles["Section"],
    )
)

limitations = [
    "The results depend on the exact dataset and workload definitions used.",
    "Managed cloud databases and locally hosted databases may not have identical hardware or network conditions.",
    "Free-tier resource limits can differ between platforms.",
    "Client-library overhead may contribute to measured latency.",
    "Database indexing and configuration can affect lookup performance.",
    "Caching and warm-state behavior can affect repeated measurements.",
    "A single dataset size does not establish performance for all graph sizes.",
    "The benchmark measures selected workloads rather than every possible graph database operation.",
    "Measured performance should not be interpreted as a universal ranking.",
    "Root-cause explanations should be supported by query plans or system documentation where possible.",
]

for item in limitations:
    add_bullet(item)


# ============================================================
# 23. FUTURE IMPROVEMENTS
# ============================================================

story.append(
    Paragraph(
        "23. Recommended Improvements Before Final Submission",
        styles["Section"],
    )
)

future_items = [
    "Generate a single five-database latency CSV containing all platforms.",
    "Generate a single five-database mixed-workload CSV containing all platforms.",
    "Regenerate the charts so that ArangoDB appears in every comparison chart.",
    "Add database version, deployment type, region and resource information to the README.",
    "Pin exact Python dependency versions in requirements.txt.",
    "Create .env.example without real passwords.",
    "Add a one-command benchmark runner.",
    "Add warm-versus-cold measurements if time permits.",
    "Repeat the complete benchmark independently to assess variance.",
    "Add standard deviation to the latency result matrix if required.",
    "Document any platform-specific query differences.",
    "Commit only reproducible source code and non-sensitive benchmark artifacts.",
]

for item in future_items:
    add_bullet(item)


# ============================================================
# 24. CONCLUSION
# ============================================================

story.append(
    Paragraph(
        "24. Conclusion",
        styles["Section"],
    )
)

story.append(
    Paragraph(
        "This project developed a practical and reproducible framework for "
        "evaluating graph database performance. The implementation progressed "
        "from dataset preparation and database connectivity through automated "
        "data loading, graph construction, latency benchmarking, concurrency "
        "testing, CSV result generation and visualization.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "The original four-database experiment showed FalkorDB achieving the "
        "lowest measured latency and highest mixed-workload throughput among "
        "FalkorDB, Neo4j Aura, Memgraph and CognoDB under the tested "
        "configuration.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "ArangoDB was subsequently implemented as the fifth database. Its "
        "dataset was successfully loaded and verified at 169,870 nodes and "
        "100,000 relationships. The completed ArangoDB benchmark measured "
        "node count, relationship count, indexed lookup, 1-hop, 2-hop and "
        "3-hop latency, together with mixed read/write throughput at "
        "concurrency levels 1, 10 and 40.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "The most important final step is therefore not another database "
        "installation, but consolidation: all five platforms should be "
        "represented in one consistent results matrix, with the same required "
        "metrics, clearly documented resource conditions and honest caveats. "
        "Once this consolidation, dependency pinning and README work is "
        "completed, the repository will be much closer to a submission-ready "
        "benchmark package.",
        styles["Body2"],
    )
)


# ============================================================
# 25. GITHUB DELIVERABLES
# ============================================================

story.append(
    Paragraph(
        "25. GitHub Submission Deliverables",
        styles["Section"],
    )
)

deliverables = [
    "Benchmark source code.",
    "Database connector implementations.",
    "Dataset loading scripts.",
    "Benchmark workload runners.",
    "CSV result files.",
    "Comparison and analysis scripts.",
    "Performance charts.",
    "Pinned requirements.txt.",
    ".env.example containing variable names only.",
    "README with complete reproducibility instructions.",
    "README results matrix covering all five databases.",
    "Methodology and fairness documentation.",
    "Environment and resource specifications.",
    "Dataset description.",
    "Limitations and caveats.",
    "Final PDF technical report.",
]

for item in deliverables:
    add_bullet(item)

story.append(Spacer(1, 8))

story.append(
    Paragraph(
        "Repository: github.com/Hanifa246/four-database-graph-benchmark",
        styles["Body2"],
    )
)


# ============================================================
# FOOTER
# ============================================================

def add_page_number(canvas, doc):
    canvas.saveState()

    canvas.setFont("Helvetica", 7.5)

    canvas.drawCentredString(
        A4[0] / 2,
        23,
        f"Five-Database Graph Benchmark | Page {doc.page}",
    )

    canvas.restoreState()


# ============================================================
# BUILD PDF
# ============================================================

doc.build(
    story,
    onFirstPage=add_page_number,
    onLaterPages=add_page_number,
)

print("=" * 70)
print("FIVE-DATABASE GRAPH BENCHMARK REPORT CREATED")
print("=" * 70)
print(f"Output: {OUTPUT_FILE}")