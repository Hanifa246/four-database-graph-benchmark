import os
from dotenv import load_dotenv
from arango import ArangoClient

load_dotenv()

host = os.getenv("ARANGO_HOST")
username = os.getenv("ARANGO_USERNAME")
password = os.getenv("ARANGO_PASSWORD")

print("=" * 60)
print("ARANGODB CONNECTION TEST")
print("=" * 60)

client = ArangoClient(hosts=host)

db = client.db(
    "_system",
    username=username,
    password=password
)

print("Connected to ArangoDB")
print("Version:", db.version())

print("=" * 60)
print("CONNECTION SUCCESSFUL")
print("=" * 60)