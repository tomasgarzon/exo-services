from django.apps import apps as global_apps
from django.conf import settings
from django.contrib.contenttypes.management import create_contenttypes
from django.db import DEFAULT_DB_ALIAS


def post_migrate_create_user_permissions(
        app_config,
        verbosity=2,
        interactive=True,
        using=DEFAULT_DB_ALIAS,
        apps=global_apps, **kwargs):

    # Ensure that contenttypes are created for this app.
    create_contenttypes(
        app_config,
        verbosity=verbosity,
        interactive=interactive,
        using=using,
        apps=apps,
        **kwargs)

    try:
        app_config = apps.get_app_config(app_config.label)
        ContentType = apps.get_model('contenttypes', 'ContentType')
        Permission = apps.get_model('auth', 'Permission')
        User = apps.get_model('auth_uuid', 'UserUUID')
        ctype = ContentType.objects.get_for_model(User, for_concrete_model=False)
        all_perms = set(Permission.objects.filter(content_type=ctype).values_list(
            'content_type', 'codename'
        ))

        searched_perms = []
        for perm in settings.AUTH_USER_ALL_PERMISSIONS:
            searched_perms.append((ctype, perm))

        perms = [
            Permission(codename=codename, name=name, content_type=ct)
            for ct, (codename, name) in searched_perms
            if (ct.pk, codename) not in all_perms
        ]

        Permission.objects.bulk_create(perms)

    except LookupError:
        pass
