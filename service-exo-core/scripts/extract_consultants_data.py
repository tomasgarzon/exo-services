import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from consultant.models import Consultant
from exo_attributes.models import ExOAttribute
from keywords.models import Keyword
from industry.models import Industry
from ratings.models import Rating


PERSONAL_DATA_FILENAME = 'consultant_data_exp/personal_data_{}.csv'
ROLES_DATA_FILENAME = 'consultant_data_exp/roles_data_{}.csv'
LANGUAGES_DATA_FILENAME = 'consultant_data_exp/languages_data_{}.csv'
ATTRIBUTES_DATA_FILENAME = 'consultant_data_exp/attributes_expertise_data_{}.csv'
RATINGS_DATA_FILENAME = 'consultant_data_exp/ratings_data_{}.csv'
CERTIFICATES_DATA_FILENAME = 'consultant_data_exp/certificates_data_{}.csv'


def generate_csv():

    print('generate personal data')
    create_personal_data()
    print('generate roles')
    create_roles()
    print('generate languages')
    create_languages()
    print('generate attributes')
    create_attributes_expertise()
    print('generate ratings')
    create_ratings()
    print('generate certifications')
    create_certificates()


def generate_user_description(consultant):
    return '{}#{}'.format(consultant.user.full_name, consultant.user.email)


def create_personal_data():
    file_name = PERSONAL_DATA_FILENAME.format(datetime.datetime.now().date())
    file = open(file_name, 'w')
    headers = ['Name', 'Email', 'Phone', 'Country', 'City', 'Nº Projects', 'MTP']
    file.write('{}\n'.format('#'.join(headers)))

    for consultant in Consultant.objects.all():
        file.write(
            '{}#{}#{}#{}#{}#{}\n'.format(
                generate_user_description(consultant),
                consultant.user.phone,
                consultant.user.country,
                consultant.user.city,
                consultant.projects.count(),
                consultant.exo_profile.personal_mtp,
            )
        )

    file.close()


def create_roles():
    file_name = ROLES_DATA_FILENAME.format(datetime.datetime.now().date())
    file = open(file_name, 'w')

    headers = ['Name', 'Email', 'Role', 'Type of Project', 'Name of the Project']
    file.write('{}\n'.format('#'.join(headers)))

    for consultant in Consultant.objects.all():
        for role in consultant.roles.all():
            file.write(
                '{}#{}#{}#{}\n'.format(
                    generate_user_description(consultant),
                    role.role,
                    role.project.type_project,
                    role.project,
                )
            )
    file.close()


def create_languages():
    file_name = LANGUAGES_DATA_FILENAME.format(datetime.datetime.now().date())
    file = open(file_name, 'w')

    headers = ['Name', 'Email', 'Language']
    file.write('{}\n'.format('#'.join(headers)))

    for consultant in Consultant.objects.all():
        for lang in consultant.languages.all():
            file.write(
                '{}#{}\n'.format(
                    generate_user_description(consultant),
                    lang,
                )
            )
    file.close()


def create_attributes_expertise():
    file_name = ATTRIBUTES_DATA_FILENAME.format(datetime.datetime.now().date())
    file = open(file_name, 'w')

    headers = ['Name', 'Email', 'Level1', 'Level2', 'Level3', 'Proficiency']
    file.write('{}\n'.format('#'.join(headers)))

    for consultant in Consultant.objects.all():
        _create_exo_attr('I', file, consultant)
        _create_exo_attr('S', file, consultant)
        _create_expertise('Expertise', file, consultant)
        _create_expertise('Technology', file, consultant)
        _create_industries(file, consultant)

    file.close()


def _create_exo_attr(attr, file, consultant):
    attribute_category = 'Ideas' if attr == 'I' else 'Scale'

    attrs = ExOAttribute.objects.filter(_type=attr).values_list('name', flat=True)
    for consultant_attr_name in attrs:
        level = 0
        try:
            level = consultant.exo_attributes.get(
                exo_attribute__name=consultant_attr_name).level
            file.write(
                '{}#ExO Attribute Skills#{}#{}#{}\n'.format(
                    generate_user_description(consultant),
                    attribute_category,
                    consultant_attr_name,
                    level,
                )
            )
        except ObjectDoesNotExist:
            pass


def _create_expertise(expertise, file, consultant):
    attrs = Keyword.objects.filter(
        tags=expertise).order_by('name').values_list('name', flat=True)
    for consultant_attr_name in attrs:
        level = 0
        try:
            level = consultant.keywords.get(
                keyword__name=consultant_attr_name).level
        except ObjectDoesNotExist:
            pass
        file.write(
            '{}#Areas of expertise#{}#{}#{}\n'.format(
                generate_user_description(consultant),
                expertise,
                consultant_attr_name,
                level,
            )
        )


def _create_industries(file, consultant):
    industries = Industry.objects.all().order_by(
        'name').values_list('name', flat=True)
    for industry in industries:
        level = 0
        try:
            level = consultant.industries.get(industry__name=industry).level
        except ObjectDoesNotExist:
            pass
        file.write(
            '{}#Areas of expertise#Industry#{}#{}\n'.format(
                generate_user_description(consultant),
                industry,
                level,
            )
        )


def create_ratings():
    file_name = RATINGS_DATA_FILENAME.format(datetime.datetime.now().date())
    file = open(file_name, 'w')

    headers = ['Name', 'Email', 'Project', 'Category', 'Roles', 'Rating']
    file.write('{}\n'.format('#'.join(headers)))

    consultant_ct = ContentType.objects.get_for_model(Consultant.objects.first())

    for consultant in Consultant.objects.all():
        ratings = Rating.objects.filter(
            object_id=consultant.pk,
            content_type=consultant_ct,
        )
        for rating in ratings:
            context_obj = rating.context_object
            if hasattr(context_obj, 'project'):
                project = context_obj.project
            elif hasattr(context_obj, 'team'):
                project = context_obj.team.project
            roles = consultant.roles.filter(
                project=project,
            ).values_list('role__name', flat=True)
            file.write(
                '{}#{}#{}#{}#{}\n'.format(
                    generate_user_description(consultant),
                    project,
                    rating.get_category_display(),
                    ','.join(roles),
                    rating.rating,
                )
            )
    file.close()


def create_certificates():
    file_name = CERTIFICATES_DATA_FILENAME.format(datetime.datetime.now().date())
    file = open(file_name, 'w')

    headers = ['Name', 'Email', 'Certification', 'Status']
    file.write('{}\n'.format('#'.join(headers)))

    for consultant in Consultant.objects.all():
        for certificate in consultant.get_certificates():
            file.write(
                '{}#{}#{}\n'.format(
                    generate_user_description(consultant),
                    certificate.name,
                    certificate.get_status_display(),
                )
            )
    file.close()
