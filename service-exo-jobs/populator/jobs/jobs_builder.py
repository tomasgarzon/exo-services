from populate.populator.builder import Builder

from exo_role.models import ExORole, Category

from jobs.models import Job


class JobBuilder(Builder):

    def create_object(self):
        category = Category.objects.get(code=self.data.get('category'))
        exo_role = ExORole.objects.get(code=self.data.get('exo_role'))
        return Job.objects.create(
            uuid=self.data.get('uuid'),
            user=self.data.get('user'),
            title=self.data.get('title'),
            start=self.data.get('start'),
            end=self.data.get('end'),
            category=category,
            exo_role=exo_role,
            url=self.data.get('url'),
            status=self.data.get('status'))
