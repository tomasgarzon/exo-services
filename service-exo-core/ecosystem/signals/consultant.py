from ecosystem.models import Member

from ..signals_define import ecosystem_member_created_signal


def post_save_consultant(sender, consultant, *args, **kwargs):
    member, _ = Member.objects.get_or_create(user=consultant.user)
    ecosystem_member_created_signal.send(
        sender=member.__class__,
        member=member)
