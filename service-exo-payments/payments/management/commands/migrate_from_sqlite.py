import sqlite3

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import Payment


class Command(BaseCommand):
    help = 'Migrate payments from sqlite database'

    def add_arguments(self, parser):
        parser.add_argument(
            'database', type=str, help='Indicates the filename database')
        parser.add_argument(
            'uuid', type=str, help='Indicates the UUID for the user who will have created all the payments')

    def handle(self, *args, **kwargs):
        database = kwargs.get('database')
        uuid = kwargs.get('uuid')
        user, _ = get_user_model().objects.get_or_create(
            uuid=uuid)
        settings.POPULATOR_MODE = True
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info(landing_payment)')
        columns = cursor.fetchall()
        column_names = []
        for column in columns:
            column_names.append([column[1], column[0]])
        cursor.execute('SELECT * FROM landing_payment')
        for row in cursor.fetchall():
            data = {}
            for name, position in column_names:
                data[name] = row[position]
            data.pop('created_by_id')
            data.pop('id')
            data['created_by'] = user
            payment = Payment.objects.create(**data)
            Payment.objects.filter(id=payment.pk).update(
                created=data['created'],
                modified=data['modified'])
