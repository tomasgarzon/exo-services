from django.db import models


class LanguageManager(models.Manager):
    use_for_related_fields = True

    def update_languages(self, user_from, languages_name):
        languages = []
        for name in languages_name:
            try:
                language = self.get_queryset().filter(name=name)[0]
            except IndexError:
                language = self.create(
                    name=name,
                )
            languages.append(language)
        return languages
