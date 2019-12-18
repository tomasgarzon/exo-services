import glob
import os
import json
import csv
from functools import reduce  # forward compatibility for Python 3
import operator

from django.core.management.base import BaseCommand


def merge(origin, new_dict, path=None):
    """merges b into origin"""
    if path is None:
        path = []
    for key in new_dict:
        if key in origin:
            if isinstance(origin[key], dict) and isinstance(new_dict[key], dict):
                merge(origin[key], new_dict[key], path + [str(key)])
            elif origin[key] == new_dict[key]:
                pass  # same leaf value
            elif isinstance(new_dict[key], dict):
                origin[key] = {}
                merge(origin[key], new_dict[key], path + [str(key)])
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            origin[key] = new_dict[key]
    return origin


def string_to_dict(keys):
    outdict = {}
    curdict = outdict
    for k in keys:
        curdict[k] = {}
        curdict = curdict[k]
    return outdict


class Command(BaseCommand):

    def add_arguments(self, parser):
        # folder name where we can read es.json, en.json, pt.json, etc original ones
        parser.add_argument('input', type=str)
        # filename csv where we will read differents translations
        parser.add_argument('csv', type=str)
        # folder name where we will create a new json files with the translations
        parser.add_argument('output', type=str)

    def handle(self, *args, **options):

        filename = options.get('csv')
        dir_name = options.get('input')
        output_name = options.get('output')
        self.stdout.write(
            self.style.SUCCESS('Reading CSV from "%s"...' % filename),
        )
        self.stdout.write(
            self.style.SUCCESS('Reading json from "%s"...' % dir_name),
        )

        translations = {}
        # read json files, original ones
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
                translations[language] = content
        languages = list(translations.keys())

        # read csv and merge the content with json files
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                key = row.get('KEY')
                for l in languages:
                    value = row.get(l)
                    key_path = key.split('.')
                    key_path.insert(0, l)
                    key_name = key_path[-1]
                    try:
                        reduce(operator.getitem, key_path[:-1], translations)[key_name] = value
                    except Exception:
                        self.stdout.write(
                            self.style.WARNING('Key error: "%s"...' % key_path),
                        )
                        new_dict = string_to_dict(key_path)
                        merge(translations, new_dict)
                        reduce(operator.getitem, key_path[:-1], translations)[key_name] = value
        # create the new files for each language
        for l in languages:
            with open(os.path.join(output_name, '{}.json'.format(l)), 'w') as file:
                file.write(json.dumps(translations[l]))
        self.stdout.write(
            self.style.SUCCESS('Successfully json created in "%s"' % output_name),
        )
