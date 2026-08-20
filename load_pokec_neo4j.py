import pandas as pd
from neo4j import GraphDatabase

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "MyNeo4jBenchmark2026!"

CSV_FILE = "data/processed/pokec_100k_edges.csv"
BATCH_SIZE = 20000

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def create_constraint(driver):
    with driver.session() as session:
        session.run("""
            CREATE CONSTRAINT user_id_unique IF NOT EXISTS
            FOR (u:User)
            REQUIRE u.id IS UNIQUE
        """)


def load_batch(tx, rows):
    query = """
    UNWIND $rows AS row

    MERGE (source:User {id: toInteger(row.source)})
    MERGE (target:User {id: toInteger(row.target)})
    MERGE (source)-[:KNOWS]->(target)
    """

    tx.run(query, rows=rows)


try:
    print("Connecting to Neo4j...")
    driver.verify_connectivity()
    print("Connected to Neo4j!")

    print("Creating index/constraint...")
    create_constraint(driver)
    print("Constraint ready!")

    print("Reading CSV...")
    df = pd.read_csv(CSV_FILE)

    print(f"Dataset loaded: {len(df):,} edges")

    with driver.session() as session:

        total = len(df)

        for start in range(0, total, BATCH_SIZE):

            batch = df.iloc[start:start + BATCH_SIZE]

            rows = batch[
                ["source", "target"]
            ].to_dict("records")

            session.execute_write(
                load_batch,
                rows
            )

            loaded = min(start + BATCH_SIZE, total)

            print(f"Loaded {loaded:,}/{total:,} edges")

    print("\nDataset successfully loaded into Neo4j!")

finally:
    driver.close()