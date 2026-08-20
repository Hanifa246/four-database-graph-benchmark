import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

try:
    driver.verify_connectivity()
    print("Connected to Neo4j successfully!")

    with driver.session() as session:
        result = session.run(
            'RETURN "Python is connected to Neo4j!" AS message'
        )
        print(result.single()["message"])

finally:
    driver.close()