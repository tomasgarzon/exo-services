from django.core.management.base import BaseCommand
from django.conf import settings

from keywords.models import Keyword

from ...models import Industry


CH_INDUSTRIES_LIST = (
    'Accommodations',
    'Accounting',
    'Advertising',
    'Aerospace',
    'Agriculture & Agribusiness',
    'Air Transportation',
    'Apparel & Accessories',
    'Auto',
    'Banking',
    'Beauty & Cosmetics',
    'Biotechnology',
    'Chemical',
    'Communications',
    'Computer',
    'Construction',
    'Consulting',
    'Consumer Products',
    'Education',
    'Electronics',
    'Employment',
    'Energy',
    'Entertainment & Recreation',
    'Fashion',
    'Financial Services',
    'Food & Beverage',
    'Health',
    'Information',
    'Journalism & News',
    'Legal Services',
    'Manufacturing',
    'Media & Broadcasting',
    'Motion Pictures & Video',
    'Music',
    'Pharmaceutical',
    'Publishing',
    'Real Estate',
    'Retail',
    'Service',
    'Sports',
    'Telecommunications',
    'Utilities',
    'Video Game',
    'Web Services',
)


class Command(BaseCommand):
    help = 'Update industries from file'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('data', nargs='+', type=str)

    def handle(self, *args, **options):
        filename = options.get('data')[0]
        self.stdout.write(
            self.style.SUCCESS('Reading file from "%s"...' % filename),
        )
        with open(filename) as f:
            industries = f.readlines()
            cleaned_industries = []
            for industry_name in industries:
                industry_name = industry_name.replace('\n', '')
                cleaned_industries.append(industry_name)
                industry, _ = Industry.objects.get_or_create(name=industry_name)
                keyword, _ = Keyword.objects.get_or_create(
                    name=industry_name,
                    public=True,
                )
                keyword.tags.add(settings.KEYWORDS_CH_INDUSTRY)
            for industry_name in CH_INDUSTRIES_LIST:
                if industry_name not in cleaned_industries:
                    self.stdout.write(
                        self.style.SUCCESS('we have to remove "%s"...' % industry_name),
                    )
                    try:
                        Industry.objects.get(name=industry_name).delete()
                    except Industry.DoesNotExist:
                        pass
                    try:
                        Keyword.objects.get(name=industry_name, public=True).delete()
                    except Keyword.DoesNotExist:
                        pass
            self.stdout.write(
                self.style.SUCCESS('Final list of industries "%s"' % cleaned_industries),
            )
