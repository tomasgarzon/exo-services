from populate.populator.builder import Builder

from circles.models import Circle
from consultant.models import Consultant


class CirclesBuilder(Builder):

    def create_object(self):
        circle = self.create_circle(
            name=self.data.get('name'),
            description=self.data.get('description'),
            code=self.data.get('code'))
        self.add_users(circle, self.data.get('followers'))
        return circle

    def create_circle(self, name, description, code):
        circle, _ = Circle.objects.get_or_create(
            name=name,
            description=description,
            code=code)
        return circle

    def add_users(self, circle, followers):
        for follower in followers:
            if isinstance(follower, Consultant):
                follower = follower.user
            circle.add_user(follower)
