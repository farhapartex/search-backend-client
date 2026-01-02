from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from engine.serializers import SearchRequestSerializer
from engine.services import SearchService
from engine.result import ServiceResult
from user.authentication import JWTAuthentication


class SearchView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_service = SearchService()

    def post(self, request):
        serializer = SearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            data = self.search_service.search(
                platforms=serializer.validated_data['platforms'],
                query=serializer.validated_data['query'],
                max_results=serializer.validated_data.get('max_results', 20)
            )
            result = ServiceResult.ok(data=data, message="Search completed")
            return Response(result.to_dict(), status=status.HTTP_200_OK)

        except Exception as e:
            result = ServiceResult.fail(message=str(e))
            return Response(result.to_dict(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
