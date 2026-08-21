import os
from dotenv import load_dotenv
from arango import ArangoClient

load_dotenv()


class ArangoDBConnector:

    def __init__(self):
        self.host = os.getenv("ARANGO_HOST", "http://localhost:8529")
        self.username = os.getenv("ARANGO_USERNAME", "root")
        self.password = os.getenv("ARANGO_PASSWORD")
        self.database_name = "_system"

        if not self.password:
            raise ValueError(
                "ARANGO_PASSWORD is not set in the .env file"
            )

        self.client = ArangoClient(hosts=self.host)

        self.db = self.client.db(
            self.database_name,
            username=self.username,
            password=self.password
        )

    def test_connection(self):
        return self.db.version()

    def close(self):
        self.client.close()


if __name__ == "__main__":

    print("=" * 60)
    print("ARANGODB CONNECTOR TEST")
    print("=" * 60)

    connector = ArangoDBConnector()

    try:
        version = connector.test_connection()

        print("Connected to ArangoDB")
        print(f"Version: {version}")

        print("=" * 60)
        print("CONNECTION SUCCESSFUL")
        print("=" * 60)

    finally:
        connector.close()