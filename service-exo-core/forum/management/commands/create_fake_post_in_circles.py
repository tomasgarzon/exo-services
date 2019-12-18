from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from actstream.models import followers

from circles.models import Circle
from utils.faker_factory import faker
from utils.random import random
from consultant.models import Consultant
from keywords.models import Keyword

from ...models import Post

User = get_user_model()


class Command(BaseCommand):
    help = (
        'Create random post and aswers for each circle'
    )

    def handle(self, *args, **options):
        self.stdout.write('\n Creating Post/Answers for testing: \n\n')
        consultants = Consultant.objects.all()
        for circle in Circle.objects.all():
            users = followers(circle)
            if len(users) < 5:
                for consultant in set(random.choices(consultants, k=random.randint(2, 10))):
                    circle.add_user(consultant.user)
                users = followers(circle)
            for i in range(random.randint(2, 10)):
                user = random.choices(users, k=1)[0]
                post = Post.objects.create_circle_post(
                    user_from=user,
                    circle=circle,
                    title=' '.join(faker.words()),
                    description=faker.text(),
                    tags=random.choices(
                        Keyword.objects.all(), k=random.randint(2, 6)),
                )
                for consultant in set(random.choices(consultants, k=random.randint(2, 10))):
                    post.see(consultant.user)
                for consultant in set(random.choices(consultants, k=random.randint(2, 10))):
                    post.see(consultant.user)
                    post.reply(consultant.user, faker.text())
        self.stdout.write('\n Finish!! \n\n')
