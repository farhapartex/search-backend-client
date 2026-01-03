from engine.grpc_client import SearchGrpcClient
from engine.mappers import SearchResponseMapper
from engine.repositories import SearchHistoryRepository
from engine.exceptions import SearchServiceException


class SearchService:

    def __init__(self, grpc_client=None, response_mapper=None, search_history_repository=None):
        self.grpc_client = grpc_client or SearchGrpcClient()
        self.response_mapper = response_mapper or SearchResponseMapper()
        self.search_history_repository = search_history_repository or SearchHistoryRepository()

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

    def save_search_history(self, user, platforms, query, max_results):
        search_history = self.search_history_repository.create(
            user=user,
            platforms=platforms,
            query=query,
            max_results=max_results
        )

        return {
            'history_id': str(search_history.id),
            'user_id': str(search_history.user.id),
            'platforms': search_history.platforms,
            'query': search_history.query,
            'max_results': search_history.max_results,
            'created_at': search_history.created_at.isoformat()
        }
