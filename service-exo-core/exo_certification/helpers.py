from certification.models import CertificationGroup
from exo_role.models import ExORole


def update_group_consultant_roles(group, new_role_code):
    new_role = ExORole.objects.get(code=new_role_code)
    consultants = group.consultant_role_group.first().consultant_roles.all()
    consultants.update(role=new_role)
    print('{} consultant roles have been succesfully renamed!'.format(consultants.count()))


def rename_certification(new_name, origin_type, target_type=None):
    if not target_type:
        target_type = origin_type
    groups = CertificationGroup.objects.filter(_type=origin_type)
    consultant_role_groups_renamed = 0
    groups_renamed = 0

    print('\n\nRenaming {} certification groups to {} ({})'.format(
        origin_type, target_type, new_name))
    for group in groups:
        group._type = target_type
        group.name = new_name
        group.save()
        groups_renamed += 1
        consultant_role_group = group.consultant_role_group.first()
        consultant_role_group.name = new_name
        consultant_role_group._type = target_type
        consultant_role_group.save()
        consultant_role_groups_renamed += 1

    print('{} groups have been succesfully renamed!'.format(groups_renamed))
    print('{} consultant_role_groups have been succesfully renamed!'.format(consultant_role_groups_renamed))
