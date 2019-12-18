from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from test_utils.test_case_mixins import UserTestMixin
from test_utils import DjangoRestFrameworkTestCase


class TestLocationCityCountry(
        UserTestMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()
        self.create_user()

    def test_city_and_country_extract(self):
        # Prepare test
        test_cases = [
            {
                'city': 'Madrid',
                'state': '',
                'country': 'Spain',
                'separator': ', ',
            },
            {
                'city': 'Madrid',
                'state': '',
                'country': 'Spain',
                'separator': '- ',
            },
            {
                'city': '',
                'state': '',
                'country': 'Spain',
                'separator': '',
            },
            # City, State, Country format
            {
                'city': 'Bangalore',
                'state': 'Karnataka',
                'country': 'India',
                'separator': ', ',
            },
        ]

        for case in test_cases:
            user = FakeUserFactory(
                location='{}{}{}{}{}'.format(
                    case.get('city'),
                    case.get('separator'),
                    case.get('state'),
                    case.get('separator'),
                    case.get('country'),
                )
            )

            self.assertEqual(user.city, case.get('city'))
            self.assertEqual(user.country, case.get('country'))
