from ..models import Member


def update_ecosystem_handler(sender, user, *args, **kwargs):
    member, _ = Member.objects.get_or_create(user=user)
    member.update_num_projects()
