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
print("             CLEAR COGNODB")
print("=" * 60)

try:

    driver.verify_connectivity()

    print("✅ Connected to CognoDB")

    with driver.session() as session:

        result = session.run("""
            MATCH (n)
            DETACH DELETE n
        """)

        result.consume()

    print("✅ Existing benchmark data removed")

    with driver.session() as session:

        nodes = session.run("""
            MATCH (n)
            RETURN count(n) AS count
        """).single()["count"]

        relationships = session.run("""
            MATCH ()-[r]->()
            RETURN count(r) AS count
        """).single()["count"]

    print()
    print("Remaining nodes:", nodes)
    print("Remaining relationships:", relationships)

finally:

    driver.close()

print()
print("=" * 60)
print("                    DONE")
print("=" * 60)