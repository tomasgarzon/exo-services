import requests

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.conf import settings

from celery import Task

from industry.models import Industry

FIELD_PUBLIC_PROFILE_URL = 'publicProfileUrl'
FIELD_USERNAME = 'username'
FIELD_HEADLINE = 'headline'
FIELD_SUMMARY = 'summary'
FIELD_INDUSTRY = 'industry'
FIELD_LOCATION = 'location'
FIELD_PICTUREURL = 'pictureUrl'


class MatchingLinkedinTask(Task):
    name = 'MatchingLinkedinTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        # short_name, full_name, location, short_me, about_me, industries, picture_profile, linkedin url
        user_id = kwargs.get('user_id')
        user = get_user_model().objects.get(pk=user_id)
        consultant = user.consultant
        response = kwargs.get('response')
        # add linkedin url
        consultant.linkedin = response.get(FIELD_PUBLIC_PROFILE_URL)
        # headline to short_me
        user.short_me = response.get(FIELD_HEADLINE)
        # summary to bio_me
        user.bio_me = response.get(FIELD_SUMMARY)
        user.location = response.get(FIELD_LOCATION)
        user.save()

        # matching industry
        try:
            Industry.objects.get(name=response.get(FIELD_INDUSTRY))
            # storing industry not supported
        except Industry.DoesNotExist:
            pass

        # picture
        url = response.get(FIELD_PICTUREURL)
        if url:
            r = requests.get(url)
            content_file = ContentFile(r.content)
            user.profile_picture.save(
                '{}.png'.format(user.get_letter_initial()),
                content_file,
                False,
            )
            user.profile_picture_origin = settings.EXO_ACCOUNTS_PROFILE_PICTURE_CH_LINKEDIN
            user.save()
