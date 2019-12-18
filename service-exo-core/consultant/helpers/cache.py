from consultant.models.consultant_profile_requirement import ConsultantProfileRequirement

from .checkers import (
    check_keyword_for_consultant,
    check_languages_for_consultant,
    check_summary_for_user,
    check_location_for_user,
    check_profile_picture_for_user
)

__all__ = [
    'KeywordFieldFilled', 'LanguageFieldFilled',
    'ProfilePictureFieldFilled', 'SummaryFieldFilled',
    'LocationFieldFilled',
]


class ProfileFieldFilled():
    key_name = None

    def __init__(self, consultant):
        self.consultant = consultant

    def get_instance(self):
        return self.consultant

    def check(self):
        profile = ConsultantProfileRequirement()
        value = profile.get_consultant_requirement(
            self.key_name, self.consultant,
        )
        try:
            value = eval(value)
        except TypeError:
            value = None
        if value is None:
            instance = self.get_instance()
            value = self.check_field(instance)
            profile.set_consultant_requirement(
                self.key_name,
                self.consultant,
                value,
            )
        return value

    def check_field(self, instance):
        raise NotImplementedError


class KeywordFieldFilled(ProfileFieldFilled):
    key_name = ConsultantProfileRequirement.KEY_KEYWORDS

    def check_field(self, instance):
        return check_keyword_for_consultant(instance)


class LanguageFieldFilled(ProfileFieldFilled):
    key_name = ConsultantProfileRequirement.KEY_LANGUAGES

    def check_field(self, instance):
        return check_languages_for_consultant(instance)


class ProfilePictureFieldFilled(ProfileFieldFilled):
    key_name = ConsultantProfileRequirement.KEY_PROFILE_PICTURE

    def get_instance(self):
        return self.consultant.user

    def check_field(self, instance):
        return check_profile_picture_for_user(instance)


class SummaryFieldFilled(ProfileFieldFilled):
    key_name = ConsultantProfileRequirement.KEY_SUMMARY

    def get_instance(self):
        return self.consultant.user

    def check_field(self, instance):
        return check_summary_for_user(instance)


class LocationFieldFilled(ProfileFieldFilled):
    key_name = ConsultantProfileRequirement.KEY_LOCATION

    def get_instance(self):
        return self.consultant.user

    def check_field(self, instance):
        return check_location_for_user(instance)
