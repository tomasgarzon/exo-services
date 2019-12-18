import yaml
import logging

from django.conf import settings


logger = logging.getLogger('django')


def load_file(filepath):
    with open(filepath, 'r') as stream:
        try:
            return yaml.load(stream, Loader=yaml.Loader)
        except yaml.YAMLError as exc:
            logger.error(exc)


def populate(page):
    filename = '{}/data/{}.yml'.format(
        settings.BASE_DIR,
        page.page_type)

    response = load_file(filename)
    sections = response.get('sections')

    for index, section_yml in enumerate(sections):
        page.sections.create(
            name=section_yml.get('name'),
            content=section_yml.get('content'),
            description=section_yml.get('description'),
            index=index)
    return page
