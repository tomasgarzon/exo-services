from rest_framework import serializers


class StepFeedBackSummarySerializer(serializers.Serializer):
    average_rate = serializers.FloatField()
    average_feelings = serializers.IntegerField()
    total_reviewers = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    results = serializers.ListField()
    origin = serializers.IntegerField()
