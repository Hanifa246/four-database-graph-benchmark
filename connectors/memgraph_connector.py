import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


class MemgraphConnector:

    def __init__(self, uri, username=None, password=None):
        self.driver = GraphDatabase.driver(
            uri,
            auth=(username, password)
        )

    def verify(self):
        self.driver.verify_connectivity()

    def run_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(
                query,
                parameters or {}
            )
            return list(result)

    def close(self):
        self.driver.close()


def create_memgraph_connector():

    host = os.getenv("MEMGRAPH_HOST")
    port = os.getenv("MEMGRAPH_PORT")

    username = os.getenv(
        "MEMGRAPH_USERNAME",
        ""
    )

    password = os.getenv(
        "MEMGRAPH_PASSWORD",
        ""
    )

    if not host:
        raise RuntimeError(
            "MEMGRAPH_HOST is not configured in .env"
        )

    if not port:
        raise RuntimeError(
            "MEMGRAPH_PORT is not configured in .env"
        )

    uri = f"bolt+ssc://{host}:{port}"

    return MemgraphConnector(
        uri,
        username,
        password
    )