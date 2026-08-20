import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("AURA_NEO4J_URI")
USERNAME = os.getenv("AURA_NEO4J_USERNAME")
PASSWORD = os.getenv("AURA_NEO4J_PASSWORD")
DATABASE = os.getenv("AURA_NEO4J_DATABASE")

if not all([URI, USERNAME, PASSWORD, DATABASE]):
    raise RuntimeError("Aura environment variables are missing.")

print("Aura URI loaded:", URI is not None)
print("Aura username loaded:", USERNAME is not None)
print("Aura password loaded:", PASSWORD is not None)
print("Aura database loaded:", DATABASE is not None)

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

try:
    driver.verify_connectivity()
    print("Connected to Neo4j Aura successfully!")

    with driver.session(database=DATABASE) as session:
        result = session.run(
            'RETURN "Python is connected to Neo4j Aura!" AS message'
        )
        print(result.single()["message"])

finally:
    driver.close()