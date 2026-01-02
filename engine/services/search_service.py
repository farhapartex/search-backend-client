from engine.grpc_client import SearchGrpcClient
from engine.mappers import SearchResponseMapper
from engine.exceptions import SearchServiceException


class SearchService:

    def __init__(self, grpc_client=None, response_mapper=None):
        self.grpc_client = grpc_client or SearchGrpcClient()
        self.response_mapper = response_mapper or SearchResponseMapper()

    def search(self, platforms, query, max_results):
        try:
            grpc_response = self.grpc_client.federated_search(
                query=query,
                max_results=max_results,
                platforms=platforms
            )

            return self.response_mapper.to_dict(grpc_response)

        except Exception as e:
            raise SearchServiceException(f"Search failed: {str(e)}")
