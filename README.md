\# Four Graph Database Performance Benchmark



\## Overview



Performance comparison of four graph databases:



\- CognoDB

\- Neo4j Aura

\- Memgraph

\- FalkorDB



\## Dataset



Pokec-derived graph dataset:



\- Nodes: 169,870

\- Relationships: 100,000



\## Benchmarks



1\. Dataset loading

2\. Node count aggregation

3\. Indexed point lookup

4\. 1-hop traversal

5\. 2-hop traversal

6\. 3-hop traversal

7\. Mixed read/write workload



\## Experimental Configuration



Latency benchmarks:

\- Warm-up runs: 20

\- Measured runs: 100



Mixed workload:

\- Read ratio: 80%

\- Write ratio: 20%

\- Concurrency: 1, 10, 40

\- Duration: approximately 30 seconds



\## Results



FalkorDB achieved the lowest measured latency across all five latency workloads.



\### Latency



| Workload | FalkorDB | Neo4j Aura | Memgraph | CognoDB |

|---|---:|---:|---:|---:|

| Node Count | 1.41 ms | 91.21 ms | 198.75 ms | 318.71 ms |

| Point Lookup | 1.84 ms | 76.75 ms | 165.71 ms | 308.79 ms |

| 1-Hop | 4.56 ms | 77.69 ms | 174.79 ms | 324.82 ms |

| 2-Hop | 7.81 ms | 77.55 ms | 170.81 ms | 320.95 ms |

| 3-Hop | 33.52 ms | 78.06 ms | 178.80 ms | 315.52 ms |



\### Mixed Workload



| Concurrency | FalkorDB ops/s | Neo4j Aura ops/s | Memgraph ops/s | CognoDB ops/s |

|---:|---:|---:|---:|---:|

| 1 | 491.63 | 10.31 | 6.00 | 3.11 |

| 10 | 1542.55 | 119.48 | 58.08 | 22.13 |

| 40 | 1494.16 | 453.23 | 230.27 | 15.07 |



\## Generated Results



Results are available in:



results/



Important files:



\- four\_database\_comparison.csv

\- final\_four\_database\_summary.csv

\- final\_mixed\_workload\_summary.csv

\- four\_database\_performance.png

\- four\_database\_mixed\_workload.png

\- four\_database\_speedup.png



\## Conclusion



Under the tested configuration, FalkorDB produced the lowest latency and highest mixed-workload throughput among the four evaluated systems.



These results represent this specific benchmark configuration and should not be interpreted as a universal ranking of graph databases.

