class SearchResponseMapper:

    @staticmethod
    def to_dict(grpc_response):
        return {
            'results': [
                SearchResponseMapper._map_result(result)
                for result in grpc_response.results
            ],
            'total_count': grpc_response.total_count,
            'platforms_success': list(grpc_response.platforms_success),
            'platforms_timeout': list(grpc_response.platforms_timeout),
            'platforms_error': list(grpc_response.platforms_error),
            'metadata': SearchResponseMapper._map_metadata(grpc_response.metadata)
        }

    @staticmethod
    def _map_result(result):
        return {
            'platform': result.platform,
            'title': result.title,
            'snippet': result.snippet,
            'url': result.url,
            'timestamp': result.timestamp,
            'metadata': dict(result.metadata)
        }

    @staticmethod
    def _map_metadata(metadata):
        if not metadata:
            return {}

        return {
            'response_time_ms': metadata.response_time_ms,
            'platforms_queried': metadata.platforms_queried
        }
