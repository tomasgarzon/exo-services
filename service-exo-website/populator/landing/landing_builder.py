from landing.models import Page

from populate.populator.builder import Builder


class LandingBuilder(Builder):

    def create_object(self):
        sections = self.data.pop('sections', [])
        page = self.create_page(**self.data)

        self.create_sections(
            page=page,
            sections=sections)
        return page

    def create_sections(self, page, sections):
        page.sections.all().delete()
        for index, section in enumerate(sections):
            page.sections.create(
                name=section.get('name'),
                description=section.get('description'),
                content=section.get('content'),
                index=index,
            )
        return page

    def create_page(self, *args, **kwargs):
        return Page.objects.create(**kwargs)
