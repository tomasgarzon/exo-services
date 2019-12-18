from django.db import models
from django.db import transaction


class InvoiceSerie(models.Model):
    prefix = models.CharField(max_length=5)
    current = models.IntegerField(default=1)

    @property
    def code(self):
        return '{}{}'.format(self.prefix, self.current.__str__().zfill(4))

    @classmethod
    def create(cls, prefix):
        with transaction.atomic():
            invoice_serie = cls.objects.filter(prefix=prefix).last()
            if not invoice_serie:
                invoice_serie = cls(prefix=prefix, current=0)
            invoice_serie.id = None
            invoice_serie.current += 1
            invoice_serie.save()
            return invoice_serie.code
