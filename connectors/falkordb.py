from falkordb import FalkorDB


class FalkorDBConnector:

    def __init__(
        self,
        host="localhost",
        port=6379,
        graph_name="benchmark"
    ):
        self.db = FalkorDB(
            host=host,
            port=port
        )

        self.graph = self.db.select_graph(
            graph_name
        )

    def verify(self):
        result = self.graph.query(
            "RETURN 1 AS test"
        )

        return result.result_set

    def run_query(
        self,
        query,
        parameters=None
    ):
        parameters = parameters or {}

        result = self.graph.query(
            query,
            params=parameters
        )

        return result.result_set

    def close(self):
        pass


def create_falkordb_connector():

    return FalkorDBConnector()