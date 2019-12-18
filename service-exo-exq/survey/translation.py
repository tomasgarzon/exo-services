from modeltranslation.translator import register, TranslationOptions
from .models import Question, Option


@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Option)
class OptionTranslationOptions(TranslationOptions):
    fields = ('value',)
