from rest_framework import serializers


class SearchRequestSerializer(serializers.Serializer):
    platforms = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        allow_empty=False
    )
    query = serializers.CharField(required=True, max_length=500, min_length=1)
    max_results = serializers.IntegerField(required=False, default=20, min_value=1, max_value=100)

    def validate_platforms(self, value):
        allowed_platforms = ['github', 'stackoverflow', 'reddit']
        for platform in value:
            if platform.lower() not in allowed_platforms:
                raise serializers.ValidationError(
                    f"Invalid platform: {platform}. Allowed platforms: {', '.join(allowed_platforms)}"
                )
        return [p.lower() for p in value]

    def validate_query(self, value):
        if not value.strip():
            raise serializers.ValidationError("Query cannot be empty or whitespace only")
        return value.strip()


class SearchHistoryQuerySerializer(serializers.Serializer):
    limit = serializers.IntegerField(required=False, default=50, min_value=1, max_value=100)
