import csv

from typing import List

from django.contrib.auth import get_user_model

from exo_accounts.utils.util import normalize_email


class UserForBulkCreation:

    def __init__(self, name, email, coins):
        self.name = name if name != '' else None
        self.email = email if email != '' else None
        self.coins = coins if coins != '' else None

    def __str__(self):
        return '{} - {} - {}'.format(self.name, self.email, self.coins)

    @property
    def exists(self) -> bool:
        return get_user_model().objects.filter(emailaddress__email=self.email).exists()

    @property
    def user(self) -> get_user_model():
        return get_user_model().objects.filter(emailaddress__email=self.email).first()

    @property
    def has_coins(self):
        return self.coins is not None

    def has_achievement_created(self) -> bool:
        return self.user.achievements.exists()

    def missing_information(self):
        return self.name is None or self.email is None


def read_name_email_coins_from_csv(content) -> List[UserForBulkCreation]:
    users = list()

    reader = csv.DictReader(content, delimiter=',')
    for row in reader:
        name = row.get('Name', None)
        email = normalize_email(row.get('Email', None))
        coins = row.get('Coins', None)
        new_user = UserForBulkCreation(name, email, coins)
        users.append(new_user)
    return users
