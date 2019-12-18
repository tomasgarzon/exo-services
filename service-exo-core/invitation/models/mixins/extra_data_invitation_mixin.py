class ExtraDataInvitationMixin:

    def extra_data(self, user_from):
        data = {}
        if self.is_signup:
            user = self.validation_object.content_object
            data = {'email': user.email}
        elif self.is_agreement:
            if hasattr(self.validation_object, 'content_object'):
                user_agreement = self.validation_object.content_object
            else:
                user_agreement = self.validation_object
            data = {
                'text': user_agreement.agreement.html,
                'file': user_agreement.agreement.file_url,
                'name': user_agreement.agreement.name,
            }
        elif self.is_on_boarding:
            consultant = self.validation_object.content_object
            data = {
                'profile_picture': consultant.user.profile_picture.get_thumbnail_url()
                if consultant.user.profile_picture else '',
                'profile_picture_origin': consultant.user.profile_picture_origin,
                'full_name': consultant.user.full_name,
                'short_name': consultant.user.short_name,
                'location': consultant.user.location,
                'place_id': consultant.user.place_id,
                'languages': [{'id': lang.pk, 'text': str(lang)} for lang in consultant.languages.all()],
                'short_me': consultant.user.short_me,
                'bio_me': consultant.user.bio_me,
            }
        return data
