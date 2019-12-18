from django.conf import settings


OPENEXO_PK = 1


class UserProfileWrapper:
    user = None

    def __init__(self, user):
        self.user = user

    @property
    def account_url(self):
        return settings.FRONTEND_USER_ACCOUNTS_PAGE.format(
            pk=self.user.pk)

    @property
    def profile_url(self):
        return settings.FRONTEND_USER_PROFILE_PAGE.format(
            pk=self.user.pk)

    @property
    def profile_slug_url(self):
        return settings.FRONTEND_USER_PROFILE_PAGE.format(
            pk=self.user.slug)

    @property
    def edit_profile_slug_url(self):
        return settings.FRONTEND_USER_PROFILE_EDIT_PAGE.format(
            **{'slug': self.user.slug, 'section': 'summary'})

    @property
    def profile_directory_slug_url(self):
        return settings.FRONTEND_USER_PROFILE_DIRECTORY_PAGE.format(
            **{'section': 'directory', 'slug': self.user.slug})

    @property
    def profile_public_slug_url(self):
        return settings.FRONTEND_USER_PROFILE_PUBLIC_PAGE.format(
            **{'slug': self.user.slug})

    @property
    def organization(self):
        user_organization = self.user.organizations_roles.first()
        if user_organization:
            return user_organization.organization
        return None

    @property
    def is_openexo_member(self):
        return self.user.organizations_roles.filter(organization_id=OPENEXO_PK).exists()

    @property
    def hubs(self):
        return self.user.hubs.all().order_by('hub__name').exclude_consulting()
