class SearchService:

    def __init__(self):
        pass

    def search(self, platforms, query, max_results):
        return {
            'platforms': platforms,
            'query': query,
            'max_results': max_results,
            'results': [],
            'total_count': 0,
            'message': 'Search service not yet implemented'
        }
