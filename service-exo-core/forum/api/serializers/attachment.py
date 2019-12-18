from rest_framework import serializers

from files.models import UploadedFile


class ForumAttachmentSerializer(serializers.ModelSerializer):
    filename = serializers.CharField()
    mimetype = serializers.CharField()
    url = serializers.URLField()

    class Meta:
        model = UploadedFile
        fields = ['pk', 'filename', 'mimetype', 'url']
