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
    KeepTogether,
)
from pathlib import Path


# ============================================================
# FILE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

OUTPUT_FILE = RESULTS_DIR / "Four_Database_Graph_Benchmark_Report.pdf"

PERFORMANCE_GRAPH = RESULTS_DIR / "four_database_performance.png"
SPEEDUP_GRAPH = RESULTS_DIR / "four_database_speedup.png"
MIXED_GRAPH = RESULTS_DIR / "four_database_mixed_workload.png"


# ============================================================
# DOCUMENT SETUP
# ============================================================

doc = SimpleDocTemplate(
    str(OUTPUT_FILE),
    pagesize=A4,
    rightMargin=45,
    leftMargin=45,
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
        fontSize=20,
        leading=25,
        spaceAfter=12,
    )
)

styles.add(
    ParagraphStyle(
        name="SubtitleCenter",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10.5,
        leading=15,
        spaceAfter=18,
    )
)

styles.add(
    ParagraphStyle(
        name="Section",
        parent=styles["Heading1"],
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=8,
    )
)

styles.add(
    ParagraphStyle(
        name="SubSection",
        parent=styles["Heading2"],
        fontSize=11,
        leading=14,
        spaceBefore=8,
        spaceAfter=6,
    )
)

styles.add(
    ParagraphStyle(
        name="Body2",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=7,
    )
)

styles.add(
    ParagraphStyle(
        name="Small",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
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


story = []


# ============================================================
# TITLE PAGE
# ============================================================

story.append(
    Spacer(1, 0.35 * inch)
)

story.append(
    Paragraph(
        "Four-Database Graph Benchmark",
        styles["TitleCenter"],
    )
)

story.append(
    Paragraph(
        "Performance Benchmarking of CognoDB, Neo4j Aura, "
        "Memgraph, and FalkorDB Using Graph Workloads",
        styles["SubtitleCenter"],
    )
)

story.append(
    Spacer(1, 0.15 * inch)
)

intro_table = Table(
    [
        ["Project", "Four-Database Graph Benchmark"],
        ["Databases", "CognoDB, Neo4j Aura, Memgraph, FalkorDB"],
        ["Dataset", "Pokec 100K-edge processed graph dataset"],
        ["Latency Runs", "100 runs per workload/database"],
        ["Mixed Workload", "80% Read / 20% Write"],
        ["Concurrency", "1, 10, and 40 workers"],
        ["Date", "21 August 2026"],
    ],
    colWidths=[1.55 * inch, 4.45 * inch],
)

intro_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8eef7")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
    )
)

story.append(intro_table)

story.append(Spacer(1, 0.3 * inch))

story.append(
    Paragraph(
        "This report summarizes the completed experimental benchmark "
        "comparing four graph database systems across aggregation, "
        "indexed lookup, graph traversal, and mixed read/write workloads.",
        styles["Body2"],
    )
)

story.append(PageBreak())


# ============================================================
# 1. INTRODUCTION
# ============================================================

story.append(
    Paragraph("1. Introduction", styles["Section"])
)

story.append(
    Paragraph(
        "Graph databases are designed to represent entities and relationships "
        "and to efficiently support operations such as graph traversal, indexed "
        "lookup, aggregation, and concurrent workloads. This project evaluates "
        "four graph database systems under a common benchmark methodology.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "The systems evaluated are CognoDB, Neo4j Aura, Memgraph, and FalkorDB. "
        "The benchmark focuses on measured latency and throughput under the "
        "selected experimental configuration rather than making a universal "
        "claim about database performance.",
        styles["Body2"],
    )
)


# ============================================================
# 2. OBJECTIVES
# ============================================================

story.append(
    Paragraph("2. Objectives", styles["Section"])
)

objectives = [
    "Compare query latency across four graph database systems.",
    "Measure node-count aggregation performance.",
    "Measure indexed point-lookup performance.",
    "Measure 1-hop, 2-hop, and 3-hop graph traversal latency.",
    "Evaluate mixed read/write throughput under different concurrency levels.",
    "Calculate performance gaps and speedups relative to CognoDB.",
    "Produce reproducible CSV summaries and performance visualizations.",
]

for item in objectives:
    story.append(
        Paragraph(
            "• " + item,
            styles["Body2"],
        )
    )


# ============================================================
# 3. DATASET AND EXPERIMENTAL SETUP
# ============================================================

story.append(
    Paragraph(
        "3. Dataset and Experimental Setup",
        styles["Section"],
    )
)

setup_data = [
    ["Parameter", "Value"],
    ["Dataset", "Pokec 100K-edge processed dataset"],
    ["Relationships", "100,000"],
    ["Unique nodes", "169,870"],
    ["Databases", "CognoDB, Neo4j Aura, Memgraph, FalkorDB"],
    ["Latency workloads", "Aggregation, indexed lookup, 1/2/3-hop traversal"],
    ["Latency repetitions", "100 runs per workload"],
    ["Mixed workload duration", "30 seconds"],
    ["Read ratio", "80%"],
    ["Write ratio", "20%"],
    ["Concurrency levels", "1, 10, 40"],
]

setup_table = Table(
    setup_data,
    colWidths=[2.2 * inch, 3.8 * inch],
)

setup_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef7")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [colors.white, colors.HexColor("#f7f9fc")],
            ),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
    )
)

story.append(setup_table)


# ============================================================
# 4. WORKLOADS
# ============================================================

story.append(
    Paragraph("4. Benchmark Workloads", styles["Section"])
)

workloads = [
    (
        "Node-count aggregation",
        "Measures the time required to count nodes in the graph.",
    ),
    (
        "Indexed point lookup",
        "Retrieves a node using the indexed Node.id property.",
    ),
    (
        "1-hop traversal",
        "Measures traversal from a starting node to directly connected nodes.",
    ),
    (
        "2-hop traversal",
        "Measures traversal across two relationship hops.",
    ),
    (
        "3-hop traversal",
        "Measures traversal across three relationship hops.",
    ),
    (
        "Mixed workload",
        "Combines read and write operations using 80% reads and 20% writes.",
    ),
]

workload_table_data = [
    ["Workload", "Description"]
]

for name, description in workloads:
    workload_table_data.append([name, description])

workload_table = Table(
    workload_table_data,
    colWidths=[1.8 * inch, 4.2 * inch],
)

workload_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef7")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [colors.white, colors.HexColor("#f7f9fc")],
            ),
        ]
    )
)

story.append(workload_table)


# ============================================================
# 5. LATENCY RESULTS
# ============================================================

story.append(
    Paragraph("5. Latency Results", styles["Section"])
)

latency_data = [
    [
        "Workload",
        "Fastest",
        "Avg ms",
        "Slowest",
        "Avg ms",
        "Gap",
    ],
    [
        "Node count",
        "FalkorDB",
        "1.4117",
        "CognoDB",
        "318.7062",
        "225.76×",
    ],
    [
        "Indexed lookup",
        "FalkorDB",
        "1.8424",
        "CognoDB",
        "308.7935",
        "167.60×",
    ],
    [
        "1-hop",
        "FalkorDB",
        "4.5598",
        "CognoDB",
        "324.8248",
        "71.24×",
    ],
    [
        "2-hop",
        "FalkorDB",
        "7.8119",
        "CognoDB",
        "320.9539",
        "41.09×",
    ],
    [
        "3-hop",
        "FalkorDB",
        "33.5168",
        "CognoDB",
        "315.5224",
        "9.41×",
    ],
]

latency_table = Table(
    latency_data,
    colWidths=[
        1.15 * inch,
        0.9 * inch,
        0.8 * inch,
        0.9 * inch,
        0.8 * inch,
        0.7 * inch,
    ],
)

latency_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef7")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [colors.white, colors.HexColor("#f7f9fc")],
            ),
        ]
    )
)

story.append(latency_table)

story.append(Spacer(1, 8))

story.append(
    Paragraph(
        "FalkorDB recorded the lowest average latency in all five measured "
        "latency workloads. CognoDB recorded the highest average latency "
        "for each workload. The largest measured performance gap occurred "
        "for node-count aggregation at 225.76×, while the smallest occurred "
        "for 3-hop traversal at 9.41×.",
        styles["Body2"],
    )
)


# ============================================================
# PERFORMANCE GRAPH
# ============================================================

if PERFORMANCE_GRAPH.exists():

    story.append(
        Paragraph(
            "Figure 1. Four-database latency comparison",
            styles["FigureCaption"],
        )
    )

    img = Image(
        str(PERFORMANCE_GRAPH),
        width=6.4 * inch,
        height=4.1 * inch,
    )

    story.append(img)

else:

    story.append(
        Paragraph(
            "Performance graph was not found in the results directory.",
            styles["Small"],
        )
    )


# ============================================================
# 6. DETAILED LATENCY OBSERVATIONS
# ============================================================

story.append(
    Paragraph(
        "6. Detailed Latency Observations",
        styles["Section"],
    )
)

observations = [
    "FalkorDB achieved 1.4117 ms average latency for node-count aggregation.",
    "FalkorDB achieved 1.8424 ms average latency for indexed point lookup.",
    "FalkorDB recorded 4.5598 ms, 7.8119 ms, and 33.5168 ms for 1-hop, 2-hop, and 3-hop traversal respectively.",
    "Neo4j Aura consistently showed lower latency than Memgraph and CognoDB in the reported latency workloads.",
    "The FalkorDB advantage decreased with increasing traversal depth, indicating that deeper traversal was comparatively more expensive.",
]

for item in observations:
    story.append(
        Paragraph(
            "• " + item,
            styles["Body2"],
        )
    )


# ============================================================
# 7. MIXED WORKLOAD
# ============================================================

story.append(
    Paragraph(
        "7. Mixed Read/Write Workload",
        styles["Section"],
    )
)

mixed_data = [
    [
        "Concurrency",
        "FalkorDB",
        "Neo4j Aura",
        "Memgraph",
        "CognoDB",
    ],
    ["1", "491.63", "10.31", "6.00", "3.11"],
    ["10", "1542.55", "119.48", "58.08", "22.13"],
    ["40", "1494.16", "453.23", "230.27", "15.07"],
]

mixed_table = Table(
    mixed_data,
    colWidths=[
        1.0 * inch,
        1.2 * inch,
        1.2 * inch,
        1.2 * inch,
        1.2 * inch,
    ],
)

mixed_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef7")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [colors.white, colors.HexColor("#f7f9fc")],
            ),
        ]
    )
)

story.append(mixed_table)

story.append(Spacer(1, 8))

story.append(
    Paragraph(
        "FalkorDB produced the highest measured throughput at every tested "
        "concurrency level. Its throughput increased from 491.63 operations "
        "per second at concurrency 1 to 1,542.55 operations per second at "
        "concurrency 10. At concurrency 40, throughput was 1,494.16 operations "
        "per second.",
        styles["Body2"],
    )
)


# ============================================================
# MIXED WORKLOAD GRAPH
# ============================================================

if MIXED_GRAPH.exists():

    story.append(
        Paragraph(
            "Figure 2. Mixed workload throughput comparison",
            styles["FigureCaption"],
        )
    )

    img = Image(
        str(MIXED_GRAPH),
        width=6.4 * inch,
        height=4.1 * inch,
    )

    story.append(img)


# ============================================================
# 8. SPEEDUP
# ============================================================

story.append(PageBreak())

story.append(
    Paragraph(
        "8. Speedup Relative to CognoDB",
        styles["Section"],
    )
)

speed_data = [
    ["Workload", "Neo4j Aura", "Memgraph", "FalkorDB"],
    ["Node count", "3.49×", "1.60×", "225.76×"],
    ["Indexed lookup", "4.02×", "1.86×", "167.60×"],
    ["1-hop", "4.18×", "1.86×", "71.24×"],
    ["2-hop", "4.14×", "1.88×", "41.09×"],
    ["3-hop", "4.04×", "1.76×", "9.41×"],
]

speed_table = Table(
    speed_data,
    colWidths=[
        1.7 * inch,
        1.3 * inch,
        1.3 * inch,
        1.3 * inch,
    ],
)

speed_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef7")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [colors.white, colors.HexColor("#f7f9fc")],
            ),
        ]
    )
)

story.append(speed_table)

story.append(Spacer(1, 10))


# ============================================================
# SPEEDUP GRAPH
# ============================================================

if SPEEDUP_GRAPH.exists():

    story.append(
        Paragraph(
            "Figure 3. Speedup relative to CognoDB",
            styles["FigureCaption"],
        )
    )

    img = Image(
        str(SPEEDUP_GRAPH),
        width=6.4 * inch,
        height=4.1 * inch,
    )

    story.append(img)


# ============================================================
# 9. DISCUSSION
# ============================================================

story.append(
    Paragraph(
        "9. Discussion",
        styles["Section"],
    )
)

discussion = [
    "FalkorDB was the fastest system across every latency workload measured.",
    "Neo4j Aura consistently ranked ahead of Memgraph and CognoDB in the reported latency measurements.",
    "FalkorDB showed its largest relative advantage in aggregation and indexed lookup.",
    "The relative advantage of FalkorDB decreased as traversal depth increased.",
    "FalkorDB achieved the highest throughput under all tested mixed-workload concurrency levels.",
    "Neo4j Aura scaled strongly from 10 to 40 concurrent workers in the mixed workload.",
    "Memgraph produced measurable throughput under concurrency 40 but remained below Neo4j Aura and FalkorDB.",
    "CognoDB recorded the lowest measured throughput in the mixed workload.",
]

for item in discussion:
    story.append(
        Paragraph(
            "• " + item,
            styles["Body2"],
        )
    )


# ============================================================
# 10. FINAL SUMMARY
# ============================================================

story.append(
    Paragraph(
        "10. Final Benchmark Summary",
        styles["Section"],
    )
)

summary_data = [
    ["Workload", "Fastest", "Fastest Avg", "Slowest", "Slowest Avg", "Gap"],
    ["Node aggregation", "FalkorDB", "1.4117 ms", "CognoDB", "318.7062 ms", "225.76×"],
    ["Indexed lookup", "FalkorDB", "1.8424 ms", "CognoDB", "308.7935 ms", "167.60×"],
    ["1-hop", "FalkorDB", "4.5598 ms", "CognoDB", "324.8248 ms", "71.24×"],
    ["2-hop", "FalkorDB", "7.8119 ms", "CognoDB", "320.9539 ms", "41.09×"],
    ["3-hop", "FalkorDB", "33.5168 ms", "CognoDB", "315.5224 ms", "9.41×"],
]

summary_table = Table(
    summary_data,
    colWidths=[
        1.15 * inch,
        0.85 * inch,
        1.05 * inch,
        0.85 * inch,
        1.05 * inch,
        0.7 * inch,
    ],
)

summary_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef7")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.2),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [colors.white, colors.HexColor("#f7f9fc")],
            ),
        ]
    )
)

story.append(summary_table)

story.append(Spacer(1, 10))

story.append(
    Paragraph(
        "<b>Overall latency result:</b> FalkorDB was fastest in all five "
        "latency workloads.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "<b>Overall throughput result:</b> FalkorDB achieved the highest "
        "measured throughput at concurrency 1, 10, and 40.",
        styles["Body2"],
    )
)


# ============================================================
# 11. LIMITATIONS
# ============================================================

story.append(
    Paragraph(
        "11. Limitations and Reproducibility",
        styles["Section"],
    )
)

story.append(
    Paragraph(
        "The benchmark results are specific to the selected dataset, workload "
        "definitions, query implementations, deployment architecture, hardware, "
        "network conditions, database configuration, indexing strategy, and "
        "client libraries. Therefore, the measured results should not be "
        "interpreted as universal rankings of the database systems.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "For stronger scientific validation, future experiments should document "
        "hardware and software versions, database configurations, query plans, "
        "warm-up and cache conditions, and resource allocation. Multiple "
        "independent benchmark repetitions should also be reported.",
        styles["Body2"],
    )
)


# ============================================================
# 12. CONCLUSION
# ============================================================

story.append(
    Paragraph(
        "12. Conclusion",
        styles["Section"],
    )
)

story.append(
    Paragraph(
        "The completed benchmark demonstrates substantial performance "
        "differences among CognoDB, Neo4j Aura, Memgraph, and FalkorDB under "
        "the selected graph workloads. FalkorDB recorded the lowest average "
        "latency for aggregation, indexed lookup, and 1-hop, 2-hop, and "
        "3-hop traversal. It also achieved the highest measured throughput "
        "for the mixed read/write workload at all tested concurrency levels.",
        styles["Body2"],
    )
)

story.append(
    Paragraph(
        "Neo4j Aura showed a consistently strong latency profile, while "
        "Memgraph and CognoDB recorded higher latency in the evaluated "
        "workloads. These findings represent the measured behavior under "
        "the stated experimental configuration and should be interpreted "
        "within those methodological limitations.",
        styles["Body2"],
    )
)


# ============================================================
# 13. PROJECT ARTIFACTS
# ============================================================

story.append(
    Paragraph(
        "13. Project Artifacts",
        styles["Section"],
    )
)

artifacts = [
    "Benchmark Python scripts",
    "Database connector implementations",
    "CSV benchmark result files",
    "Four-database comparison data",
    "Speedup calculations",
    "Performance visualization PNG files",
    "Final benchmark summary CSV files",
    "README project documentation",
]

for item in artifacts:
    story.append(
        Paragraph(
            "• " + item,
            styles["Body2"],
        )
    )

story.append(
    Paragraph(
        "GitHub Repository: github.com/Hanifa246/four-database-graph-benchmark",
        styles["Body2"],
    )
)


# ============================================================
# FOOTER
# ============================================================

def add_page_number(canvas, doc):
    canvas.saveState()

    canvas.setFont("Helvetica", 8)

    canvas.drawCentredString(
        A4[0] / 2,
        25,
        f"Four-Database Graph Benchmark  |  Page {doc.page}",
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
print("FOUR-DATABASE GRAPH BENCHMARK REPORT CREATED")
print("=" * 70)
print(f"Output: {OUTPUT_FILE}")