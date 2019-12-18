from django.conf import settings

from utils.mail import handlers


def send_email_attendee(project, user_to):
    data = {
        'workshop_name': project.name,
        'location': project.location,
        'date': project.start.date().strftime('%d %b %Y')
    }
    handlers.mail_handler.send_mail(
        'join_workshop_attendee',
        recipients=[user_to.email],
        **data
    )
    return data


def send_email_trainer(project, user):
    data = {
        'workshop_name': project.name,
        'location': project.location,
        'date': project.start.date().strftime('%d %b %Y'),
        'public_url': settings.FRONTEND_PROJECT_PROFILE_PAGE.format(
            **{'section': 'attendees', 'slug': project.slug}),
        'participant_name': user.get_full_name(),
        'participant_email': user.email
    }
    handlers.mail_handler.send_mail(
        'join_workshop_trainer',
        recipients=[project.created_by.email],
        **data
    )
    return data
