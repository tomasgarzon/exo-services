import logging
import json

from django.core.management.base import BaseCommand

from ...models import Category, Tag

logger = logging.getLogger('library')

INDUSTRIES_CATEGORY = 'Industries'
EXO_ATTRIBUTES_CATEGORY = 'ExO Attributes'
TECH_CATEGORY = 'Technologies'

INDUSTRIES_LIST = [
    'Accommodations', 'Accounting', 'Advertising', 'Aerospace',
    'Agriculture & Agribusiness', 'Air Transportation', 'Aircraft',
    'Alcohol', 'Apparel & Accessories', 'Auto', 'Aviation', 'Banking',
    'Beauty & Cosmetics', 'Big Data', 'Biotechnology', 'Biotechnology',
    'Chemical', 'Communications', 'Computer', 'Construction',
    'Consulting', 'Consumer Products', 'Cosmetic', 'Cybersecurity',
    'Diamond',
    'Economy', 'Education', 'Electronics', 'Employment', 'Energy', 'Ethics',
    'Entertainment & Recreation',
    'Fashion', 'Financial Services', 'Food & Beverage', 'Future',
    'Glass', 'Health',
    'Hospitality',
    'Information',
    'Insurance', 'Inspiration', 'Internet of Things', 'Investment and Trading',
    'Journalism & News',
    'Legal Services', 'Life Sciences', 'Manufacturing',
    'Media & Broadcasting', 'Medical', 'Metal', 'Military',
    'Motion Pictures & Video', 'Music', 'Nanotechnology',
    'Neuroscience', 'Nuclear', 'Packaging', 'Paint & Coatings',
    'Oil and Gas',
    'Petrochemicals', 'Pharmaceutical', 'Plastics', 'Privacy', 'Private Spaceflight',
    'Publishing', 'Pulp & Paper', 'Rail', 'Real Estate', 'Recycling',
    'Retail', 'Robotics', 'Security', 'Service', 'Shipping', 'Shipyards',
    'Society', 'Solar', 'Space', 'Space-based Economy', 'Specialty Drugs',
    'Sporting Goods', 'Sports', 'Steel', 'Sustainability',
    'Telecommunications', 'Television', 'Textile', 'Tire', 'Tobacco', 'Toy', 'Transport',
    'Utilities',
    'Video Game',
    'Waste', 'Web Services',
]

EXO_ATTRIBUTES_LIST = [
    "Staff on Demand", "Community & Crowd", "Algorithms",
    "Leveraged Assets", "Engagement", "Interfaces", "Dashboards",
    "Experimentation", "Autonomy", "Social Technologies", 'MTP'
]


DEFAULT_FILTERS = [
    'Consulting', 'Education', 'Computer', 'Communications',
    'Blockchain', 'Internet of Things', 'Artificial general intelligence',
    'Cryptocurrency', 'Virtual Reality'
]


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        TECHNOLOGIES = []
        with open('resource/management/commands/technologies.json') as json_data:
            techs = json.load(json_data)

        for tech in techs:
            TECHNOLOGIES.append(tech.get("title"))

        CATEGORIES = [{
            'name': EXO_ATTRIBUTES_CATEGORY,
            'values': EXO_ATTRIBUTES_LIST
        }, {
            'name': INDUSTRIES_CATEGORY,
            'values': INDUSTRIES_LIST
        }, {
            'name': TECH_CATEGORY,
            'values': TECHNOLOGIES
        }]

        for category in CATEGORIES:
            category_name = category.get("name")
            cat, _ = Category.objects.get_or_create(name=category_name)
            Tag.objects.get_or_create(name=category.get("name"))
            default_show_filter = False

            for tag in category.get("values"):
                default_show_filter = False
                if category_name == EXO_ATTRIBUTES_CATEGORY or tag in DEFAULT_FILTERS:
                    default_show_filter = True

                defaults = {
                    'category': cat,
                    'default_show_filter': default_show_filter
                }
                Tag.objects.update_or_create(name=tag, defaults=defaults)
