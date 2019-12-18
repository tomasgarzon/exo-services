from rest_framework import serializers

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from exo_accounts.models import EmailAddress

from ....models import UserProjectRole


class UserProjectRoleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.get_full_name')
    email = serializers.EmailField(source='user.email')
    exo_role = serializers.CharField(read_only=True)

    class Meta:
        model = UserProjectRole
        fields = ['name', 'email', 'exo_role', 'status', 'pk']

    def validate_email(self, value):
        exo_role = self.context.get('request').data.get('exo_role')

        if exo_role == settings.EXO_ROLE_CODE_SPRINT_OTHER:
            is_superuser = get_user_model().objects.filter(
                email=value,
                is_superuser=True).exists()

            if not is_superuser:
                raise ValidationError('User must have superuser perms.')

        return value

    def create(self, validated_data):
        exo_role = self.context.get('request').data.get('exo_role')

        project = validated_data.get('project')
        user_from = validated_data.get('user_from')
        user_data = validated_data.get('user')

        name = user_data.get('get_full_name')
        email = user_data.get('email')

        if exo_role == settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT:
            new_user = project.add_user_project_member(
                user_from=user_from, name=name, email=email)
        elif exo_role == settings.EXO_ROLE_CODE_SPRINT_OBSERVER:
            new_user = project.add_user_project_supervisor(
                user_from=user_from, name=name, email=email)
        elif exo_role == settings.EXO_ROLE_CODE_SPRINT_OTHER:
            new_user = project.add_user_project_staff(
                user_from=user_from, name=name, email=email)
        elif exo_role == settings.EXO_ROLE_CODE_DELIVERY_MANAGER:
            new_user = project.add_user_project_delivery_manager(
                user_from=user_from, name=name, email=email)

        return project.users_roles.filter_by_user(new_user) \
            .filter_by_exo_role_code(exo_role).get()

    def update(self, instance, validated_data):
        user = instance.user
        user_data = validated_data.get('user')
        email = user_data.get('email')
        email_valid = EmailAddress.objects.add_user_email(
            user, email)
        if email_valid:
            email_address = EmailAddress.objects.get(email=email)
            email_address.set_primary()
            user.refresh_from_db()
            user.full_name = user_data.get('get_full_name')
            user.short_name = user_data.get('get_full_name').split(' ')[0]
            user.save()
        else:
            new_user = get_user_model().objects.get(
                emailaddress__email=email)
            instance.user = new_user
            instance.save()
        return instance


class UploadUserProjectRoleSerializer(serializers.Serializer):
    content = serializers.CharField()
    exo_role = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    class Meta:
        fields = ['content', 'exo_role']

    def create(self, validated_data):
        user_from = validated_data.get('user_from')
        project = validated_data.get('project')
        data = validated_data.get('content')
        exo_role = validated_data.get('exo_role')

        user_list = data.splitlines()
        users = []

        for user in user_list:
            name, email = user.split(',')

            if exo_role == settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT:
                project.add_user_project_member(
                    user_from=user_from, name=name, email=email)
            elif exo_role == settings.EXO_ROLE_CODE_SPRINT_OBSERVER:
                project.add_user_project_supervisor(
                    user_from=user_from, name=name, email=email)
            elif exo_role == settings.EXO_ROLE_CODE_SPRINT_OTHER:
                project.add_user_project_staff(
                    user_from=user_from, name=name, email=email)
            elif exo_role == settings.EXO_ROLE_CODE_DELIVERY_MANAGER:
                project.add_user_project_delivery_manager(
                    user_from=user_from, name=name, email=email)

            users.append(email)

        return project.users_roles \
            .filter(user__email__in=users) \
            .filter_by_exo_role_code(exo_role)
