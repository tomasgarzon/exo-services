from rest_framework import serializers

from ...models import Invitation


class InvitationRetrieveSerializer(serializers.ModelSerializer):
    extra_data = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = ['extra_data', 'status', 'type']

    def get_extra_data(self, obj):
        data = {}

        if obj.is_signup:
            user = obj.validation_object.content_object

            data = {
                'email': user.email
            }
        elif obj.is_agreement:
            if hasattr(obj.validation_object, 'content_object'):
                user_agreement = obj.validation_object.content_object
            else:
                user_agreement = obj.validation_object

            data = {
                'file': user_agreement.agreement.file_url,
                'name': user_agreement.agreement.name,
                'text': user_agreement.agreement.html,
            }
        elif obj.is_on_boarding:
            consultant = obj.validation_object.content_object

            data = {
                'profile_picture': consultant.user.profile_picture.get_thumbnail_url()
                if consultant.user.profile_picture else '',
                'profile_picture_origin': consultant.user.profile_picture_origin,
                'full_name': consultant.user.full_name,
                'short_name': consultant.user.short_name,
                'location': consultant.user.location,
                'place_id': consultant.user.place_id,
                'personal_mtp': consultant.exo_profile.personal_mtp,
            }
        return data
