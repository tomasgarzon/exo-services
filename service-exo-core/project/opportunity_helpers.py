from django.conf import settings

CH_GROUP_TEAM = 'T'  # from opportunities service
CH_CURRENCY = {
    'E': 'X',
}
CH_DURATION_UNITY = 'H'  # hour


def create_opportunity_groups(project):
    groups = []
    project_type = {
        'fastracksprint': settings.EXO_ROLE_CODE_FASTRACK_ADVISOR,
        'genericproject': settings.EXO_ROLE_CODE_ADVISOR,
        'sprint': settings.EXO_ROLE_CODE_ADVISOR,
        'sprintautomated': settings.EXO_ROLE_CODE_ADVISOR,
        'workshop': settings.EXO_ROLE_CODE_ADVISOR}
    code_advisor = project_type.get(project.type_project_lower)
    project_ticket_settings = project.ticket_settings_rel.first()
    if not project_ticket_settings:
        return
    for team in project.teams.all():
        ticket_settings = team.ticket_settings_rel.first()
        if not ticket_settings:
            continue

        team_data = {}
        team_data['origin'] = CH_GROUP_TEAM
        team_data['related_uuid'] = team.uuid.__str__()
        team_data['total'] = ticket_settings.total
        team_data['exo_role'] = code_advisor
        team_data['certification_required'] = settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS
        team_data['entity'] = project.customer.__str__()
        team_data['duration_unity'] = CH_DURATION_UNITY
        team_data['duration_value'] = 1
        if CH_CURRENCY.get(project_ticket_settings.currency):
            currency = CH_CURRENCY.get(project_ticket_settings.currency)
        else:
            currency = project_ticket_settings.currency
        managers = [team.coach.user.uuid.__str__()] + list(team.team_members.all())
        if project.project_manager:
            managers.append(project.project_manager.user.uuid.__str__())
        for user in project.delivery_managers:
            managers.append(user.uuid.__str__())
        team_data['budgets'] = [{
            'budget': project_ticket_settings.price,
            'currency': currency
        }]
        team_data['managers'] = managers
        groups.append(team_data)
    return groups
