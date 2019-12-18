from django.contrib import admin

# Register your models here.
from .models import (
    Achievement, UserAchievement,
    Reward, UserReward
)


admin.site.register(Achievement)
admin.site.register(UserAchievement)
admin.site.register(Reward)
admin.site.register(UserReward)
