from rest_framework import serializers

from custom_auth.api.serializers import UserSimpleSerializer

from ...models import UploadedFile


class UploadedFileGenericReverseSerializerMixin(serializers.Serializer):

    uploadedFile = serializers.SerializerMethodField()

    def get_uploadedFile(self, obj):
        return UploadedFileRelatedGenericSerializer(obj).data


class UploadedFileReverseSerializerMixin(serializers.Serializer):

    uploadedFile = serializers.SerializerMethodField()

    def get_uploadedFile(self, obj):
        return UploadedFileRelatedSerializer(obj).data


class UploadedFileRelatedSerializer(serializers.ModelSerializer):

    class Meta:
        model = UploadedFile
        fields = ['pk', 'filename', 'mimetype', 'url', 'version', 'filestack_status']


class UploadedFileRelatedGenericSerializer(serializers.ModelSerializer):

    type = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    iframe = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()
    created_by = UserSimpleSerializer()
    visibility = serializers.CharField(source='get_visibility_code')
    can_change_visibility = serializers.SerializerMethodField()

    class Meta:
        model = UploadedFile
        fields = [
            'pk',
            'type',
            'status',
            'name',
            'description',
            'thumbnail',
            'iframe',
            'link',
            'order',
            'filestack_status',
            'created_by',
            'visibility',
            'can_change_visibility',
        ]

    def get_type(self, obj):
        return obj.file_mimetype

    def get_status(self, obj):
        return obj.latest.filestack_status

    def get_name(self, obj):
        return obj.filename

    def get_description(self, obj):
        return ''

    def get_thumbnail(self, obj):
        return ''

    def get_iframe(self, obj):
        return ''

    def get_link(self, obj):
        return obj.url

    def get_order(self, obj):
        return ''

    def get_can_change_visibility(self, obj):
        user_from = self.context.get('request').user
        return obj.can_change_visibility(user_from)
