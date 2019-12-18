from django.core.management import BaseCommand

from circles.models import Circle


class Command(BaseCommand):

    help = (
        'Regenerate urls for circle images'
    )

    def handle(self, *args, **options):
        images = {
            'A': 'https://cdn.filestackcontent.com/t6GFHOzBQk2YHcDcK10b',
            'B': 'https://cdn.filestackcontent.com/Sp6JmkLiTYWu9QoLC6z5',
            'C': 'https://cdn.filestackcontent.com/mjtMicfQA2t1CjBcmeUl',
            'E': 'https://cdn.filestackcontent.com/y05HOa9HTXmUCu3TS34z',
            'F': 'https://cdn.filestackcontent.com/0T0kiGTpT6MR1ZlPaETA',
            'M': 'https://cdn.filestackcontent.com/xyC1jR7TOGDCsNQnzVXt',
            'T': 'https://cdn.filestackcontent.com/e5vyoTvyQEv5MjTEluXl',
            'X': 'https://cdn.filestackcontent.com/0oLMtUydSySQdBBMZvs2',
            'I': 'https://cdn.filestackcontent.com/LVJfz8WZQHOiGsft7bG3',
            'R': 'https://cdn.filestackcontent.com/35Xx0r1aQUmx8dlpbeEI',
        }

        for key in images.keys():
            try:
                circle = Circle.objects.get(code=key)
                circle.image = images.get(key)
                circle.save()
            except Circle.DoesNotExist:
                pass
