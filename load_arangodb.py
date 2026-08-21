import os
import pandas as pd
from dotenv import load_dotenv
from arango import ArangoClient

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

HOST = os.getenv("ARANGO_HOST", "http://localhost:8529")
USERNAME = os.getenv("ARANGO_USERNAME", "root")
PASSWORD = os.getenv("ARANGO_PASSWORD")

DATABASE = "_system"

GRAPH_NAME = "pokec_graph"
NODE_COLLECTION = "nodes"
EDGE_COLLECTION = "relationships"

DATASET = "data/processed/pokec_100k_edges.csv"


# ============================================================
# CONNECT TO ARANGODB
# ============================================================

def connect():

    if not PASSWORD:
        raise ValueError(
            "ARANGO_PASSWORD is not set in the .env file"
        )

    client = ArangoClient(
        hosts=HOST
    )

    db = client.db(
        DATABASE,
        username=USERNAME,
        password=PASSWORD
    )

    print("Connected to ArangoDB")
    print("Version:", db.version())

    return client, db


# ============================================================
# CLEAN OLD DATA
# ============================================================

def cleanup_old_data(db):

    print("=" * 60)
    print("CLEANING OLD ARANGODB DATA")
    print("=" * 60)

    # IMPORTANT:
    # The graph must be deleted BEFORE deleting its collections.

    if db.has_graph(GRAPH_NAME):

        print(
            "Deleting existing graph:",
            GRAPH_NAME
        )

        db.delete_graph(
            GRAPH_NAME,
            drop_collections=False
        )

        print("Old graph deleted")

    # Now it is safe to delete the collections.

    if db.has_collection(EDGE_COLLECTION):

        print(
            "Deleting old edge collection:",
            EDGE_COLLECTION
        )

        db.delete_collection(
            EDGE_COLLECTION
        )

        print("Old edge collection deleted")

    if db.has_collection(NODE_COLLECTION):

        print(
            "Deleting old node collection:",
            NODE_COLLECTION
        )

        db.delete_collection(
            NODE_COLLECTION
        )

        print("Old node collection deleted")

    print("Old data cleaned successfully")


# ============================================================
# CREATE COLLECTIONS
# ============================================================

def create_collections(db):

    print("=" * 60)
    print("CREATING COLLECTIONS")
    print("=" * 60)

    db.create_collection(
        NODE_COLLECTION
    )

    print(
        "Created node collection:",
        NODE_COLLECTION
    )

    db.create_collection(
        EDGE_COLLECTION,
        edge=True
    )

    print(
        "Created edge collection:",
        EDGE_COLLECTION
    )


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset(db):

    print("=" * 60)
    print("LOADING POKEC DATASET")
    print("=" * 60)

    if not os.path.exists(DATASET):

        raise FileNotFoundError(
            f"Dataset not found: {DATASET}"
        )

    df = pd.read_csv(
        DATASET
    )

    print(
        "Dataset rows:",
        len(df)
    )

    print(
        "Columns:",
        list(df.columns)
    )

    # --------------------------------------------------------
    # FIND UNIQUE NODES
    # --------------------------------------------------------

    source_nodes = set(
        df["source"].astype(str)
    )

    target_nodes = set(
        df["target"].astype(str)
    )

    nodes = source_nodes | target_nodes

    print(
        "Unique nodes:",
        len(nodes)
    )

    print(
        "Relationships:",
        len(df)
    )

    node_collection = db.collection(
        NODE_COLLECTION
    )

    edge_collection = db.collection(
        EDGE_COLLECTION
    )

    batch_size = 5000

    # ========================================================
    # INSERT NODES
    # ========================================================

    print("=" * 60)
    print("INSERTING NODES")
    print("=" * 60)

    node_documents = []

    for node_id in nodes:

        node_documents.append(
            {
                "_key": node_id,
                "node_id": node_id
            }
        )

    for i in range(
        0,
        len(node_documents),
        batch_size
    ):

        batch = node_documents[
            i:i + batch_size
        ]

        node_collection.insert_many(
            batch,
            overwrite=True
        )

        inserted = min(
            i + batch_size,
            len(node_documents)
        )

        print(
            f"Nodes inserted: "
            f"{inserted}/{len(node_documents)}"
        )

    # ========================================================
    # INSERT RELATIONSHIPS
    # ========================================================

    print("=" * 60)
    print("INSERTING RELATIONSHIPS")
    print("=" * 60)

    edge_documents = []

    for index, row in df.iterrows():

        source = str(
            row["source"]
        )

        target = str(
            row["target"]
        )

        edge_documents.append(
            {
                "_key": str(index),
                "_from": (
                    f"{NODE_COLLECTION}/{source}"
                ),
                "_to": (
                    f"{NODE_COLLECTION}/{target}"
                )
            }
        )

        if len(edge_documents) >= batch_size:

            edge_collection.insert_many(
                edge_documents,
                overwrite=True
            )

            print(
                f"Relationships inserted: "
                f"{index + 1}/{len(df)}"
            )

            edge_documents = []

    # Insert remaining relationships

    if edge_documents:

        edge_collection.insert_many(
            edge_documents,
            overwrite=True
        )

    print(
        "Relationships inserted:",
        len(df)
    )


# ============================================================
# CREATE GRAPH
# ============================================================

def create_graph(db):

    print("=" * 60)
    print("CREATING GRAPH")
    print("=" * 60)

    graph = db.create_graph(
        GRAPH_NAME
    )

    graph.create_edge_definition(
        edge_collection=EDGE_COLLECTION,
        from_vertex_collections=[
            NODE_COLLECTION
        ],
        to_vertex_collections=[
            NODE_COLLECTION
        ]
    )

    print(
        "Graph created:",
        GRAPH_NAME
    )


# ============================================================
# VERIFY DATA
# ============================================================

def verify(db):

    print("=" * 60)
    print("VERIFYING ARANGODB DATA")
    print("=" * 60)

    node_count = db.collection(
        NODE_COLLECTION
    ).count()

    edge_count = db.collection(
        EDGE_COLLECTION
    ).count()

    print(
        "Nodes:",
        node_count
    )

    print(
        "Relationships:",
        edge_count
    )

    print("=" * 60)

    if edge_count == 100000:

        print(
            "DATA LOAD SUCCESSFUL"
        )

    else:

        print(
            "WARNING: Expected 100000 relationships"
        )

    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

def main():

    client = None

    try:

        # Connect
        client, db = connect()

        # Remove previous graph and collections
        cleanup_old_data(db)

        # Create fresh collections
        create_collections(db)

        # Load Pokec dataset
        load_dataset(db)

        # Create graph
        create_graph(db)

        # Verify
        verify(db)

    except Exception as e:

        print("=" * 60)
        print("ERROR")
        print("=" * 60)

        print(e)

        raise

    finally:

        if client:

            client.close()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()