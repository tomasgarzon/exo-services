from django.conf import settings


def check_keyword_for_consultant(consultant) -> bool:
    return consultant.total_keywords_attributes_industries >= settings.ACHIEVEMENT_KEYWORDS_FOR_UNLOCK


def check_languages_for_consultant(consultant) -> bool:
    return consultant.languages.count() > 0


def check_summary_for_user(user) -> bool:
    return user.bio_me is not None and user.bio_me != ''


def check_location_for_user(user) -> bool:
    return user.location is not None


def check_profile_picture_for_user(user) -> bool:
    return not user.has_profile_picture_default
