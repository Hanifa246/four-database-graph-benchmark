import os
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")


TEST_NODE = 1438694


driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

print("=" * 60)
print("             COGNODB TRAVERSAL TEST")
print("=" * 60)

try:

    driver.verify_connectivity()

    print("✅ Connected")

    with driver.session() as session:

        print()
        print("Testing 1-hop...")

        start = time.perf_counter()

        result = session.run("""
            MATCH (p:Person {id: $id})
                  -[:FRIEND]->(friend)
            RETURN count(friend) AS result
        """, id=TEST_NODE)

        value = result.single()["result"]

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        print(
            f"1-hop result: {value}"
        )

        print(
            f"1-hop time: {elapsed:.2f} ms"
        )


        print()
        print("Testing 2-hop...")

        start = time.perf_counter()

        result = session.run("""
            MATCH (p:Person {id: $id})
                  -[:FRIEND*2]->(friend)
            RETURN count(DISTINCT friend) AS result
        """, id=TEST_NODE)

        value = result.single()["result"]

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        print(
            f"2-hop result: {value}"
        )

        print(
            f"2-hop time: {elapsed:.2f} ms"
        )


        print()
        print("Testing 3-hop...")

        start = time.perf_counter()

        result = session.run("""
            MATCH (p:Person {id: $id})
                  -[:FRIEND*3]->(friend)
            RETURN count(DISTINCT friend) AS result
        """, id=TEST_NODE)

        value = result.single()["result"]

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        print(
            f"3-hop result: {value}"
        )

        print(
            f"3-hop time: {elapsed:.2f} ms"
        )


except Exception as e:

    print()
    print("❌ Traversal test failed:")
    print(type(e).__name__)
    print(e)

finally:

    driver.close()

print()
print("=" * 60)
print("                    FINISHED")
print("=" * 60)