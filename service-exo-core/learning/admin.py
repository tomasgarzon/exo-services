from django.contrib import admin


# Register your models here.
from .models import Resource, TrainingSession, MicroLearning

admin.site.register(Resource)
admin.site.register(TrainingSession)
admin.site.register(MicroLearning)
