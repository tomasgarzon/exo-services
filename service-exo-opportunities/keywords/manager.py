from django.db import models


class KeywordManager(models.Manager):
    use_for_related_fields = True

    def update_keywords(self, user_from, keywords_name):
        keywords = []
        for name in keywords_name:
            try:
                keyword = self.get_queryset().filter(name=name)[0]
            except IndexError:
                keyword = self.create(
                    name=name,
                    created_by=user_from,
                    public=False,
                )
            keywords.append(keyword)
        return keywords
