from django.contrib import admin

# Register your models here.
from . import models


admin.site.register(models.Survey)
admin.site.register(models.SurveyFilled)
admin.site.register(models.Question)
admin.site.register(models.Option)
admin.site.register(models.Answer)
admin.site.register(models.Result)
