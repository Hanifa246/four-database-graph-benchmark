import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

username = os.getenv("MEMGRAPH_USERNAME")
password = os.getenv("MEMGRAPH_PASSWORD")
host = os.getenv("MEMGRAPH_HOST")
port = os.getenv("MEMGRAPH_PORT")

uri = f"bolt+ssc://{host}:{port}"

print("=" * 60)
print("MEMGRAPH CONNECTION TEST")
print("=" * 60)
print(f"Host: {host}")
print(f"Port: {port}")
print(f"Username: {username}")
print(f"URI: {uri}")

try:
    driver = GraphDatabase.driver(
        uri,
        auth=(username, password)
    )

    driver.verify_connectivity()

    print("\nSUCCESS: Connected to Memgraph!")

    with driver.session() as session:
        result = session.run(
            'RETURN "Memgraph is working!" AS message'
        )
        record = result.single()
        print(record["message"])

except Exception as e:
    print("\nCONNECTION FAILED")
    print(type(e).__name__)
    print(e)

finally:
    try:
        driver.close()
    except:
        pass