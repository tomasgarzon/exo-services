
class EntityManagerMixin:

    def get_queryset(self):
        return self.queryset_class(
            self.model,
            using=self._db,
        )
