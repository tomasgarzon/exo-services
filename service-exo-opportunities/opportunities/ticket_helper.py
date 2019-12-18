from django.contrib.auth import get_user_model
from django.conf import settings

from .models import Opportunity, Applicant, ApplicantSow
from .signals.conversations import start_converation_for_applicant_handler


User = get_user_model()


def get_user_created(logs):
    for log in logs:
        if log['status'] == 'X':
            return log['user']
    return None


def create_opportunity_from_ticket(**kwargs):
    user_from = get_user_created(kwargs['history'])
    opp = Opportunity.objects.create_opportunity_in_group(
        user_from, kwargs.get('group'),
        draft=True,
        _status=kwargs.get('status'),
        title=kwargs.get('title'),
        description=kwargs.get('description'),
        keywords=kwargs.get('keywords'),
        languages=kwargs.get('languages'),
        mode=kwargs.get('mode'),
        target=kwargs.get('target'),
        users_tagged=kwargs.get('users_tagged'),
        deadline_date=kwargs.get('deadline_date'),
        start_date=kwargs.get('deadline_date'),
        uuid=kwargs.get('uuid'),
        slug=kwargs.get('slug'),
        sent_at=kwargs.get('created'),
        files=kwargs.get('files', [])
    )
    opp.history.create(
        user=user_from,
        status=settings.OPPORTUNITIES_CH_REQUESTED)
    Opportunity.objects.filter(pk=opp.pk).update(
        created=kwargs.get('created'),
        modified=kwargs.get('created'))
    opp.history.update(
        created=kwargs.get('created'),
        modified=kwargs.get('created'))

    opp.status = (user_from, settings.OPPORTUNITIES_CH_CLOSED)

    for app in kwargs.get('applicants', []):
        applicant = Applicant.objects.create(
            user=app.get('user'),
            opportunity=opp,
            summary=app.get('summary'),
            status=app.get('status'))
        applicant.history.update(
            created=kwargs.get('created'),
            modified=kwargs.get('created'))
        Applicant.objects.filter(pk=applicant.pk).update(
            created=kwargs.get('created'),
            modified=kwargs.get('created'))
        start_converation_for_applicant_handler(
            Applicant, opp, applicant)
        if app.get('slot'):
            when = app.get('slot')
            ApplicantSow.objects.create(
                applicant=applicant,
                title=opp.title,
                description=opp.description,
                start_date=when.date(),
                end_date=when.date(),
                start_time=when.time(),
            )
    applicant_selected = opp.applicants_selected.first()
    if applicant_selected:
        for rating in kwargs.get('ratings'):
            applicant_selected.feedbacks.create(
                created_by=rating['user'],
                explained=rating['rating'],
                collaboration=rating['rating'],
                communication=rating['rating'],
                recommendation=rating['rating'] * 2,
                comment=rating.get('comment', ''))
    return opp
