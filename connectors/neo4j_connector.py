import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


class Neo4jConnector:

    def __init__(self, uri, username, password, database):
        self.driver = GraphDatabase.driver(
            uri,
            auth=(username, password)
        )
        self.database = database

    def verify(self):
        self.driver.verify_connectivity()

    def run_query(self, query, parameters=None):
        with self.driver.session(database=self.database) as session:
            result = session.run(
                query,
                parameters or {}
            )
            return list(result)

    def close(self):
        self.driver.close()


def create_cognodb_connector():

    return Neo4jConnector(
        os.getenv("COGNODB_URI"),
        os.getenv("COGNODB_USERNAME"),
        os.getenv("COGNODB_PASSWORD"),
        os.getenv("COGNODB_DATABASE", "neo4j")
    )


def create_aura_connector():

    return Neo4jConnector(
        os.getenv("AURA_NEO4J_URI"),
        os.getenv("AURA_NEO4J_USERNAME"),
        os.getenv("AURA_NEO4J_PASSWORD"),
        os.getenv("AURA_NEO4J_DATABASE")
    )