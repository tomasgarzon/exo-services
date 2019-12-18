from django.db import router
from django.db.models.deletion import Collector


class CollectInstancesRelatedMixin:

    def get_instances_related(self, collector=None):
        using = router.db_for_write(self.__class__, instance=self)
        if not collector:
            collector = Collector(using=using)
        collector.collect([self], keep_parents=False)
        return collector
