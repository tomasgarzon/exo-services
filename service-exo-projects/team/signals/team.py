from django.contrib.contenttypes.models import ContentType
from reversion.models import Version

from ..models import Team
from ..signals_define import stream_changed


def post_save_team(sender, revision, versions, *args, **kwargs):
    team_content_type = ContentType.objects.get_for_model(Team)
    for version in versions:
        if version.content_type == team_content_type:
            instance = version.object
            manage_team_versions(instance)


def manage_team_versions(instance):
    object_versions = Version.objects.get_for_object(instance)
    previous_stream = None

    for obj_version in object_versions:
        if previous_stream and previous_stream != obj_version.field_dict.get('stream_id'):
            stream_changed.send(
                sender=instance.__class__,
                team=instance)
            break
        previous_stream = obj_version.field_dict.get('stream_id')
