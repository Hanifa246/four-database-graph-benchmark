from connectors.neo4j_connector import (
    create_cognodb_connector,
    create_aura_connector
)


def test_database(name, connector):

    try:
        connector.verify()

        result = connector.run_query(
            'RETURN "connection successful" AS message'
        )

        print(f"{name}: {result[0]['message']}")

    finally:
        connector.close()


print("=" * 60)
print("DATABASE CONNECTION TEST")
print("=" * 60)

cognodb = create_cognodb_connector()
test_database("CognoDB", cognodb)

aura = create_aura_connector()
test_database("Neo4j Aura", aura)