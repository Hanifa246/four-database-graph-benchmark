import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

print("=" * 60)
print("              COGNODB STATUS CHECK")
print("=" * 60)

try:

    driver.verify_connectivity()

    print("✅ Connected to CognoDB")

    with driver.session() as session:

        node_count = session.run("""
            MATCH (n)
            RETURN count(n) AS count
        """).single()["count"]

        relationship_count = session.run("""
            MATCH ()-[r]->()
            RETURN count(r) AS count
        """).single()["count"]

    print()
    print("Nodes:", f"{node_count:,}")
    print("Relationships:", f"{relationship_count:,}")

finally:

    driver.close()

print()
print("=" * 60)