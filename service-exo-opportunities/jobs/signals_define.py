from django.dispatch import Signal

create_job = Signal(providing_args=['applicant'])
