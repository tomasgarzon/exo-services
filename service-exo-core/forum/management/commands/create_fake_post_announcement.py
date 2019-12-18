from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from utils.faker_factory import faker
from utils.random import random
from consultant.models import Consultant
from keywords.models import Keyword

from ...models import Post

User = get_user_model()


class Command(BaseCommand):
    help = (
        'Create random announcements and answers'
    )

    def handle(self, *args, **options):
        self.stdout.write('\n Creating Announcement/Answers for testing: \n\n')
        consultants = Consultant.objects.all()
        for _ in range(random.randint(2, 10)):
            user = User.objects.filter(is_superuser=True).first()
            post = Post.objects.create_announcement_post(
                user_from=user,
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
