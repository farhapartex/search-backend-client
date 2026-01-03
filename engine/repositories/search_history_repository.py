from engine.models import SearchHistory


class SearchHistoryRepository:

    def __init__(self):
        pass

    def create(self, user, platforms, query, max_results):
        search_history = SearchHistory(
            user=user,
            platforms=platforms,
            query=query,
            max_results=max_results
        )
        search_history.save()
        return search_history

    def find_by_user(self, user, limit=50):
        return SearchHistory.objects(user=user).order_by('-created_at').limit(limit)

    def find_recent(self, limit=100):
        return SearchHistory.objects.order_by('-created_at').limit(limit)

    def count_by_user(self, user):
        return SearchHistory.objects(user=user).count()
