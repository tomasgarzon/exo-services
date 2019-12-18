import glob
import os
import json
import csv

from django.core.management.base import BaseCommand


def get_values(key, zone):
    result = {}
    for z1, z2 in zone.items():
        if isinstance(z2, dict):
            result.update(get_values('{}.{}'.format(key, z1), z2))
        else:
            result['{}.{}'.format(key, z1)] = z2
    return result


class Command(BaseCommand):

    def add_arguments(self, parser):
        # folder name where we can read es.json, en.json, pt.json, etc
        parser.add_argument('input', type=str)
        # filename where we will create a new csv file
        parser.add_argument('output', type=str)

    def handle(self, *args, **options):

        filename = options.get('output')
        dir_name = options.get('input')
        self.stdout.write(
            self.style.SUCCESS('Reading from "%s"...' % dir_name),
        )

        translations = {}
        # Read files with key as json format
        for k in glob.glob(os.path.join(dir_name, '*.json')):
            base = os.path.basename(k)
            language, extension = os.path.splitext(base)
            self.stdout.write(
                self.style.SUCCESS('Processing "%s"...' % language),
            )
            translations[language] = {}
            with open(k, 'r') as file:
                content = file.read()
                content = json.loads(content)
                for zone_key, zone_values in content.items():
                    # storing the info as SECTION.KEYNAME
                    keys = get_values(zone_key, zone_values)
                    translations[language].update(keys)
        languages = list(translations.keys())
        languages.remove('en')

        # create the csv file with header
        header = ['KEY', 'en']
        for lang in languages:
            header.append(lang)

        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            # 'en' file is required
            for key, value in translations['en'].items():
                row = [key, value]
                for lang in languages:
                    try:
                        row.append(translations[lang][key])
                    except KeyError:
                        self.stdout.write(
                            self.style.ERROR('KeyError "%s"' % key),
                        )
                writer.writerow(row)

        self.stdout.write(
            self.style.SUCCESS('Successfully csv created "%s"' % filename),
        )
