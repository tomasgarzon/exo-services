import requests
from django.core.management.base import BaseCommand

from core.models.country import Country


class Command(BaseCommand):

    def handle(self, *args, **options):
        REST_COUNTRIES_URL = 'https://restcountries.eu/rest/v2/all'
        try:
            imported_countries = 0
            response = requests.get(REST_COUNTRIES_URL)
            response.raise_for_status()
            countries = response.json()
            Country.objects.all().delete()
            for country in countries:
                Country.objects.create(
                    name=country.get('name'),
                    native_name=country.get('nativeName'),
                    code_2=country.get('alpha2Code'),
                    code_3=country.get('alpha3Code'),
                    flag=country.get('flag'),
                )
                imported_countries += 1
        except Exception as err:
            print('There was an error importing countries, skipping\n{}'.format(err))
