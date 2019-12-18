from modeltranslation.translator import register, TranslationOptions
from .models import Industry


@register(Industry)
class IndustryTranslationOptions(TranslationOptions):
    fields = ('name',)
