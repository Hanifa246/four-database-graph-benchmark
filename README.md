# Graph Database Performance Benchmark

## 1. Project Overview

This project evaluates the performance of graph databases using a common graph dataset and a consistent benchmark methodology.

The objective is to compare database performance across graph-oriented workloads such as:

* Dataset loading
* Node count aggregation
* Relationship count aggregation
* Indexed point lookup
* 1-hop graph traversal
* 2-hop graph traversal
* 3-hop graph traversal
* Mixed read/write workloads
* Concurrent workload performance

The benchmark was designed to provide a reproducible comparison while documenting the resource configuration, workload definitions, warm-up procedure, repeated measurements, concurrency levels, and limitations of the experiment.

The project currently evaluates five graph database platforms:

1. CognoDB
2. Neo4j Aura
3. Memgraph
4. FalkorDB
5. ArangoDB

The same logical Pokec-derived graph dataset is loaded into each system and equivalent workloads are executed using database-specific query languages and APIs.

---

# 2. Project Objectives

The main objectives of this project are:

1. Compare latency across multiple graph database platforms.
2. Measure graph traversal performance at different hop depths.
3. Measure indexed point-lookup performance.
4. Measure aggregation performance.
5. Evaluate mixed read/write workloads.
6. Study the effect of concurrency on throughput.
7. Perform repeated benchmark runs and report statistical measures.
8. Provide reproducible benchmark scripts.
9. Document the experimental environment and fairness considerations.
10. Analyze why the observed database performance differs.

The benchmark is intended to provide an empirical comparison under the tested configuration rather than claim a universal ranking of graph databases.

---

# 3. Databases Evaluated

## 3.1 CognoDB

CognoDB is the primary platform being evaluated in the assignment.

The benchmark evaluates CognoDB using the same logical dataset and equivalent workloads used for the other databases.

---

## 3.2 Neo4j Aura

Neo4j Aura is the managed cloud deployment of Neo4j.

It is included to provide a comparison with a widely used graph database platform operating in a managed cloud environment.

---

## 3.3 Memgraph

Memgraph is a graph database designed for high-performance graph workloads.

It is evaluated using the same dataset and equivalent graph operations.

---

## 3.4 FalkorDB

FalkorDB is a graph database based on the Redis ecosystem.

It is included because of its graph query and traversal capabilities and provides another architectural approach to graph data processing.

---

## 3.5 ArangoDB

ArangoDB is a multi-model database that supports graph workloads through vertex and edge collections and named graphs.

For this benchmark, ArangoDB was configured using:

* Node collection: `nodes`
* Edge collection: `relationships`
* Graph: `pokec_graph`

The dataset was successfully loaded with:

* 169,870 nodes
* 100,000 relationships

The ArangoDB benchmark measures the same major workload categories as the other platforms.

---

# 4. Dataset

The benchmark uses a Pokec-derived graph dataset.

The processed dataset contains:

| Property       |              Value |
| -------------- | -----------------: |
| Nodes          |            169,870 |
| Relationships  |            100,000 |
| Dataset format |                CSV |
| Edge columns   | `source`, `target` |

The primary input file is:

```text
data/processed/pokec_100k_edges.csv
```

The CSV contains two columns:

```text
source
target
```

Each row represents a directed relationship between two graph nodes.

Example:

```text
source,target
430522,1251166
89328,67842
802792,942730
217386,437738
420060,664354
```

The same logical graph structure is loaded into each database.

---

# 5. Benchmark Architecture

The project follows a common benchmark pipeline:

```text
Pokec CSV Dataset
       |
       v
Database-specific Data Loader
       |
       v
Graph Database
       |
       v
Benchmark Workload Runner
       |
       +---- Latency Measurements
       |
       +---- Mixed Read/Write Workload
       |
       +---- Concurrency Tests
       |
       v
CSV Result Files
       |
       v
Comparison Scripts
       |
       v
Tables + Charts + Analysis
```

Each database has its own connector and/or loader because graph databases use different APIs and query languages.

However, the logical operations being measured remain equivalent.

---

# 6. Benchmark Workloads

The project evaluates several workloads.

## 6.1 Dataset Loading

The dataset loader inserts the graph into the target database.

The loader records or verifies:

* Number of nodes
* Number of relationships
* Successful graph creation
* Collection/table/index configuration where applicable

For ArangoDB, the loading process successfully created:

```text
nodes
relationships
pokec_graph
```

and verified:

```text
Nodes:         169870
Relationships: 100000
```

---

## 6.2 Node Count Aggregation

This workload measures the time required to count all nodes in the graph.

Conceptually:

```text
COUNT(all nodes)
```

This measures basic aggregation performance.

---

## 6.3 Relationship Count Aggregation

This workload measures the time required to count all relationships.

Conceptually:

```text
COUNT(all relationships)
```

This provides another basic aggregation workload.

---

## 6.4 Indexed Point Lookup

This workload retrieves a specific node using its indexed identifier.

Conceptually:

```text
Find node where ID = X
```

The purpose is to measure point-access latency rather than graph traversal.

---

## 6.5 One-Hop Traversal

The benchmark starts from a selected node and retrieves directly connected nodes.

Conceptually:

```text
Start node
    |
    +---- Neighbor
```

This measures basic graph traversal performance.

---

## 6.6 Two-Hop Traversal

The benchmark traverses two relationship levels:

```text
Start
  |
  +-- Level 1
        |
        +-- Level 2
```

This measures performance when traversal depth increases.

---

## 6.7 Three-Hop Traversal

The benchmark traverses three relationship levels:

```text
Start
  |
  +-- Level 1
        |
        +-- Level 2
              |
              +-- Level 3
```

This provides a deeper traversal workload.

---

# 7. Latency Measurement Methodology

Latency benchmarks use a warm-up phase followed by measured runs.

The current benchmark configuration uses:

```text
Warm-up runs: 20
Measured runs: 100
```

Warm-up runs are used to reduce the influence of initial connection, compilation, caching, and other startup effects.

Only the measured runs are included in the reported latency statistics.

For each workload, the following metrics are calculated:

* Average
* Minimum
* Maximum
* Median
* P95

All latency values are reported in milliseconds.

---

# 8. Statistical Metrics

## Average

The average represents the arithmetic mean of the measured execution times.

It provides an overall estimate of typical latency.

## Minimum

The minimum represents the fastest observed execution.

## Maximum

The maximum represents the slowest observed execution.

## Median

The median is the middle observation after sorting all measured executions.

It is useful because it is less affected by extreme outliers than the average.

## P95

P95 represents the latency below which approximately 95% of measured executions fall.

It provides an indication of tail latency.

Reporting both average and P95 helps distinguish typical performance from slower executions.

---

# 9. Mixed Read/Write Workload

The benchmark also evaluates a mixed workload consisting of:

```text
80% reads
20% writes
```

The workload runs for approximately:

```text
30 seconds
```

Three concurrency levels are tested:

```text
1 client
10 clients
40 clients
```

The main metric is:

```text
operations per second
```

This test evaluates how database throughput changes as concurrent workload increases.

---

# 10. Concurrency Methodology

The concurrency experiment evaluates:

```text
1 client
10 clients
40 clients
```

A single client represents low-concurrency operation.

Ten clients represent moderate concurrency.

Forty clients represent a higher concurrent workload.

The purpose is not simply to find the highest throughput number, but to observe how each database scales as the number of concurrent operations increases.

---

# 11. Experimental Fairness

Fairness is an important part of the benchmark.

The benchmark attempts to maintain consistency by using:

* The same logical dataset
* The same node and relationship counts
* Equivalent workloads
* Similar warm-up procedures
* The same number of measured runs where supported
* The same concurrency levels
* The same 80/20 read/write workload
* The same approximate workload duration

The query syntax is database-specific because each graph database exposes different query languages and APIs.

Therefore, the benchmark compares equivalent operations rather than literally identical query strings.

---

# 12. Results — Four Database Comparison

The following results are from the completed four-database benchmark.

## 12.1 Latency Results

| Workload     | FalkorDB | Neo4j Aura |  Memgraph |   CognoDB |
| ------------ | -------: | ---------: | --------: | --------: |
| Node Count   |  1.41 ms |   91.21 ms | 198.75 ms | 318.71 ms |
| Point Lookup |  1.84 ms |   76.75 ms | 165.71 ms | 308.79 ms |
| 1-Hop        |  4.56 ms |   77.69 ms | 174.79 ms | 324.82 ms |
| 2-Hop        |  7.81 ms |   77.55 ms | 170.81 ms | 320.95 ms |
| 3-Hop        | 33.52 ms |   78.06 ms | 178.80 ms | 315.52 ms |

Under this completed four-database configuration, FalkorDB recorded the lowest measured average latency across all five listed latency workloads.

---

# 13. Mixed Workload Results

The completed four-database mixed workload results are:

| Concurrency | FalkorDB ops/s | Neo4j Aura ops/s | Memgraph ops/s | CognoDB ops/s |
| ----------: | -------------: | ---------------: | -------------: | ------------: |
|           1 |         491.63 |            10.31 |           6.00 |          3.11 |
|          10 |        1542.55 |           119.48 |          58.08 |         22.13 |
|          40 |        1494.16 |           453.23 |         230.27 |         15.07 |

FalkorDB achieved the highest measured throughput at all three tested concurrency levels in this four-database experiment.

---

# 14. ArangoDB Benchmark Results

ArangoDB was subsequently added as the fifth database.

The dataset was successfully loaded and verified:

```text
Nodes:         169870
Relationships: 100000
```

The completed ArangoDB latency benchmark produced:

| Workload           |    Average |
| ------------------ | ---------: |
| Node Count         | 64.5845 ms |
| Relationship Count | 54.2713 ms |
| Indexed Lookup     |  3.0577 ms |
| 1-Hop              | 46.7648 ms |
| 2-Hop              | 46.3274 ms |
| 3-Hop              | 46.4933 ms |

The ArangoDB mixed workload produced:

| Concurrency |   Throughput |
| ----------: | -----------: |
|           1 |  26.78 ops/s |
|          10 | 256.36 ops/s |
|          40 | 592.68 ops/s |

These results should be incorporated into the final five-database comparison after the corresponding final benchmark runs for all platforms have been verified under the same finalized methodology.

---

# 15. Initial Results Analysis

## 15.1 Latency

In the completed four-database comparison, FalkorDB produced the lowest measured latency for the tested aggregation, lookup, and traversal workloads.

Neo4j Aura recorded the second-lowest latency among the four systems in these measurements.

Memgraph and CognoDB recorded higher average latency under the tested configuration.

ArangoDB's measured results show particularly low indexed lookup latency at approximately 3.06 ms, while its traversal workloads were approximately 46–47 ms.

These numbers should be interpreted as measurements from the specific benchmark environment rather than universal performance rankings.

---

## 15.2 Graph Traversal

Traversal performance is especially important for graph databases.

The benchmark evaluates:

```text
1-hop
2-hop
3-hop
```

The results show that traversal latency can differ significantly between database architectures.

For the completed four-database experiment, FalkorDB remained substantially faster than the other three platforms for the tested traversal workloads.

ArangoDB showed relatively similar measured latency across the one-, two-, and three-hop tests in the current experiment.

Further analysis should consider the number of vertices returned by each traversal, graph topology, caching behavior, query execution strategy, and deployment resources.

---

## 15.3 Indexed Lookup

Indexed point lookup measures a different behavior from traversal.

The ArangoDB benchmark recorded approximately:

```text
3.06 ms
```

for indexed lookup.

The completed four-database results showed FalkorDB at:

```text
1.84 ms
```

This demonstrates why the benchmark includes multiple workload types instead of relying on a single query.

---

## 15.4 Mixed Workload

The mixed workload measures practical database activity involving both reads and writes.

The four-database experiment showed FalkorDB achieving the highest throughput at:

```text
1 client:   491.63 ops/s
10 clients: 1542.55 ops/s
40 clients: 1494.16 ops/s
```

The increase from 10 to 40 clients was not proportional, indicating that increasing concurrency does not necessarily produce unlimited throughput.

ArangoDB's measured throughput increased from:

```text
26.78 ops/s
```

at one client to:

```text
592.68 ops/s
```

at 40 clients.

This demonstrates a substantial increase in throughput as concurrency increased in the tested workload.

---

# 16. Database-by-Database Interpretation

## CognoDB

CognoDB is the primary platform being evaluated in this assignment.

Its benchmark results provide the baseline for comparison with the other graph database systems.

The benchmark focuses on identifying where CognoDB performs well and where additional optimization opportunities may exist.

---

## Neo4j Aura

Neo4j Aura provides a managed cloud graph database comparison.

Because it is a cloud-hosted service, network latency and cloud resource configuration can influence measurements.

Therefore, comparisons between Neo4j Aura and locally hosted databases must be interpreted carefully.

---

## Memgraph

Memgraph provides another graph-native architecture for comparison.

Its results allow the benchmark to distinguish performance differences between multiple graph-oriented database engines rather than comparing CognoDB with only one alternative.

---

## FalkorDB

FalkorDB produced the strongest measured performance in the completed four-database benchmark.

It recorded the lowest average latency across the listed latency workloads and the highest mixed-workload throughput at the tested concurrency levels.

These results are specific to the experimental configuration.

---

## ArangoDB

ArangoDB provides a multi-model database architecture with graph functionality.

The benchmark used an ArangoDB graph named:

```text
pokec_graph
```

with:

```text
nodes
relationships
```

as the vertex and edge collections.

Its measured indexed lookup latency was low, while traversal latency remained around 46–47 ms for the selected test node.

Its mixed workload throughput increased substantially as concurrency increased.

---

# 17. Reproducibility

The project is designed so that another user can reproduce the benchmark by following the repository instructions.

The general workflow is:

```text
1. Clone repository
2. Create Python virtual environment
3. Install dependencies
4. Configure environment variables
5. Start required database services
6. Prepare/load dataset
7. Run database-specific benchmark
8. Generate comparison results
9. Generate charts
```

Database passwords and connection URIs are not intended to be stored in Git.

Instead, configuration is read from environment variables.

Example:

```text
ARANGO_HOST=http://localhost:8529
ARANGO_USERNAME=root
ARANGO_PASSWORD=YOUR_PASSWORD_HERE
```

The actual `.env` file must remain private.

A `.env.example` file should be included in the repository as a configuration template.

---

# 18. Project Structure

The repository contains database connectors, loaders, benchmark scripts, comparison scripts, and result files.

A simplified structure is:

```text
C:\Graph
│
├── benchmarks/
│
├── connectors/
│   └── arangodb.py
│
├── data/
│   └── processed/
│       └── pokec_100k_edges.csv
│
├── results/
│
├── advanced_benchmark.py
├── advanced_benchmark_cognodb.py
├── advanced_benchmark_memgraph.py
│
├── benchmark_neo4j.py
├── benchmark_cognodb.py
├── benchmark_arangodb.py
│
├── load_cognodb.py
├── load_memgraph.py
├── load_pokec_neo4j.py
├── load_arangodb.py
│
├── create_comparison.py
├── create_four_database_comparison.py
├── calculate_speedup.py
├── calculate_four_database_speedup.py
│
├── plot_comparison.py
├── plot_comparison_log.py
├── plot_four_database_comparison.py
├── plot_four_database_speedup.py
│
├── test_cognodb.py
├── test_neo4j.py
├── test_memgraph.py
├── test_arangodb.py
│
├── requirements.txt
├── .env.example
└── README.md
```

---

# 19. Generated Results

Important result files include:

```text
results/
```

and database-specific CSV files such as:

```text
arangodb_benchmark_results.csv
arangodb_mixed_workload_results.csv
```

Previously generated comparison files include:

```text
four_database_comparison.csv
final_four_database_summary.csv
final_mixed_workload_summary.csv
overall_performance_summary.csv
three_database_comparison.csv
```

Charts include:

```text
four_database_performance.png
four_database_mixed_workload.png
four_database_speedup.png
three_database_comparison.png
three_database_performance_comparison.png
performance_ratio_comparison.png
```

---

# 20. Code Quality

The benchmark is divided into separate components rather than placing the entire experiment in a single script.

The major components are:

### Connectors

Responsible for establishing database connections.

### Loaders

Responsible for loading the Pokec-derived dataset.

### Benchmark runners

Responsible for executing workloads and collecting timing measurements.

### Comparison scripts

Responsible for combining results from different databases.

### Plotting scripts

Responsible for generating visual comparisons.

### Result files

CSV files preserve the measured benchmark data for later analysis.

This separation makes the benchmark easier to extend to additional graph databases.

---

# 21. Warm vs Measured Runs

Warm-up runs are intentionally separated from measured runs.

The warm-up phase allows the database and client environment to perform initial setup before measurements are collected.

The measured phase then executes the workload repeatedly.

This approach reduces the likelihood that first-request initialization dominates the reported latency.

For the finalized benchmark, the exact warm-up and measurement configuration should remain consistent across platforms wherever technically possible.

---

# 22. Fairness and Resource Considerations

A benchmark between graph databases is affected by the environment in which each database runs.

Important factors include:

* CPU
* RAM
* Storage
* Database configuration
* Cloud instance size
* Network latency
* Cache state
* Storage performance
* Database version
* Query planner
* Index configuration
* Free-tier limitations

The results therefore represent the tested configurations.

Where platforms use different deployment models, those differences are explicitly treated as a limitation rather than hidden.

The benchmark does not claim that the measured results represent universal database performance.

---

# 23. Caveats and Limitations

Several limitations should be considered when interpreting the results.

### 23.1 Deployment Differences

Some databases may run locally while others may use cloud-hosted infrastructure.

This can introduce network and infrastructure differences.

### 23.2 Free-Tier Restrictions

Cloud free tiers can impose restrictions on:

* CPU
* Memory
* Storage
* Connections
* Throughput

These restrictions may influence benchmark results.

### 23.3 Dataset Size

The benchmark uses a 100,000-edge graph.

Performance characteristics may change significantly for larger graphs.

### 23.4 Workload Diversity

The benchmark focuses on a selected set of graph operations.

It does not cover every possible graph database workload.

### 23.5 Query Language Differences

The databases use different query languages and execution engines.

The benchmark therefore compares logically equivalent workloads rather than identical query strings.

### 23.6 Cache Effects

Repeated benchmark runs can benefit from database caching.

Warm-up runs reduce but do not completely eliminate this effect.

### 23.7 Single Test Dataset

Using one dataset limits the generalizability of the conclusions.

Additional datasets would provide stronger evidence.

---

# 24. Why Multiple Metrics Are Necessary

No single metric is sufficient to evaluate a graph database.

For example:

* Aggregation measures basic data processing.
* Indexed lookup measures point-access performance.
* 1-hop traversal measures local graph navigation.
* 2-hop and 3-hop traversal measure deeper graph navigation.
* Mixed workloads measure practical read/write behavior.
* Concurrency tests measure scalability under simultaneous operations.

A database can perform well in one category and less well in another.

Therefore, the benchmark uses multiple workloads to provide a broader evaluation.

---

# 25. Conclusion

This project provides a reproducible benchmark framework for comparing graph database performance using a common Pokec-derived graph dataset.

The completed four-database benchmark showed that FalkorDB achieved the lowest measured latency across the listed latency workloads and the highest mixed-workload throughput among CognoDB, Neo4j Aura, Memgraph, and FalkorDB under the tested configuration.

ArangoDB was subsequently added as a fifth database. Its dataset loading and benchmark execution were successfully implemented, including latency measurements and mixed read/write concurrency tests.

The current results indicate meaningful performance differences between the tested platforms. However, the results should be interpreted in the context of the specific hardware, deployment model, database configuration, dataset size, caching behavior, and free-tier limitations.

The goal of this project is therefore not to declare a universally fastest graph database, but to provide a transparent, reproducible methodology that allows the observed performance differences to be measured and analyzed fairly.

---

# 26. Reproducing the ArangoDB Experiment

After configuring the environment variables and starting ArangoDB:

```bash
python test_arangodb.py
```

Verify the dataset:

```bash
python load_arangodb.py
```

Run the benchmark:

```bash
python benchmark_arangodb.py
```

The benchmark generates:

```text
results/arangodb_benchmark_results.csv
results/arangodb_mixed_workload_results.csv
```

The generated CSV files can then be incorporated into the overall five-database comparison.

---

# 27. Security

Credentials are intentionally excluded from the repository.

Do not commit:

```text
.env
```

The repository should contain:

```text
.env.example
```

with placeholder values only.

Example:

```text
ARANGO_HOST=http://localhost:8529
ARANGO_USERNAME=root
ARANGO_PASSWORD=YOUR_PASSWORD_HERE
```

No database passwords, private connection URIs, API keys, or other secrets should be committed to GitHub.

---

# 28. Final Project Deliverables

The completed repository is intended to contain:

* Database connectors
* Dataset loaders
* Benchmark runners
* Workload definitions
* Concurrency benchmark
* Statistical measurement code
* CSV benchmark results
* Comparison scripts
* Visualization scripts
* Reproducibility instructions
* Methodology documentation
* Results matrix
* Performance analysis
* Fairness discussion
* Caveats and limitations
* Final conclusion

This structure is designed to satisfy the major requirements of the Wexa AI graph database benchmarking assignment while keeping the experiment reproducible and extensible.
