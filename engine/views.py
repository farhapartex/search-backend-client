from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from engine.serializers import SearchRequestSerializer, SearchHistoryQuerySerializer
from engine.services import SearchService
from engine.result import ServiceResult
from engine.exceptions import SearchServiceException
from user.authentication import JWTAuthentication


class SearchView(APIView):
    authentication_classes = [JWTAuthentication]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_service = SearchService()

    def post(self, request):
        serializer = SearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        platforms = serializer.validated_data['platforms']
        query = serializer.validated_data['query']
        max_results = serializer.validated_data.get('max_results', 20)

        try:
            data = self.search_service.search(
                platforms=platforms,
                query=query,
                max_results=max_results
            )

            if request.user and request.user.is_authenticated:
                self.search_service.save_search_history(
                    user=request.user,
                    platforms=platforms,
                    query=query,
                    max_results=max_results
                )

            result = ServiceResult.ok(data=data, message="Search completed successfully")
            return Response(result.to_dict(), status=status.HTTP_200_OK)

        except SearchServiceException as e:
            result = ServiceResult.fail(message=str(e))
            return Response(result.to_dict(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchHistoryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_service = SearchService()

    def get(self, request):
        serializer = SearchHistoryQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        limit = serializer.validated_data.get('limit', 50)

        try:
            data = self.search_service.get_user_search_history(
                user=request.user,
                limit=limit
            )
            result = ServiceResult.ok(data=data, message="Search history retrieved successfully")
            return Response(result.to_dict(), status=status.HTTP_200_OK)

        except Exception as e:
            result = ServiceResult.fail(message=str(e))
            return Response(result.to_dict(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
