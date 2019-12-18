from rest_framework import serializers

from django.conf import settings

from ..models import Page, Section
from ..signals_define import signal_website_update


class SectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Section
        fields = ['name', 'content', 'index', 'description']
        read_only_fields = ['index']


class PageSerializer(serializers.ModelSerializer):

    sections = SectionSerializer(many=True)
    domain = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ['pk', 'slug', 'theme', 'sections', 'domain', 'published']
        read_only_fields = ['domain', 'published']

    def update(self, instance, validated_data):
        instance.slug = validated_data.get('slug')
        instance.theme = validated_data.get('theme')
        instance.save()
        instance.sections.all().delete()

        for index, section in enumerate(validated_data.get('sections')):
            instance.sections.create(
                name=section.get('name'),
                content=section.get('content'),
                description=section.get('description'),
                index=index)
        signal_website_update.send(
            sender=Page,
            instance=instance)
        instance.mark_as_published()
        return instance

    def get_domain(self, obj):
        return settings.EXO_WEBSITE_DOMAIN


class CreatePageSerializer(serializers.ModelSerializer):

    page_type = serializers.ChoiceField(
        required=False,
        choices=settings.LANDING_CH_PAGE_TYPES)

    class Meta:
        model = Page
        fields = ['uuid', 'slug', 'page_type']

    def create(self, validated_data):
        page = super().create(validated_data)
        page.user = self.context.get('request').user
        page.save()
        return page


class PublicPageSerializer(serializers.ModelSerializer):
    link = serializers.CharField()
    link_preview = serializers.CharField()

    class Meta:
        model = Page
        fields = ['uuid', 'link', 'published', 'link_preview']
