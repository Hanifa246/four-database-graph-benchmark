import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

print("CognoDB URI loaded:", URI is not None)
print("CognoDB username loaded:", USERNAME is not None)
print("CognoDB password loaded:", PASSWORD is not None)

if not URI or not USERNAME or not PASSWORD:
    raise RuntimeError("CognoDB environment variables are missing.")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

try:
    driver.verify_connectivity()
    print("Connected to CognoDB Cloud successfully!")

    with driver.session() as session:
        result = session.run(
            'RETURN "Python is connected to CognoDB Cloud!" AS message'
        )
        print(result.single()["message"])

finally:
    driver.close()