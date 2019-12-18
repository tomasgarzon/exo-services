from service.external.typeform import GENERIC_TYPEFORMS

from typeform_feedback.models import GenericTypeformFeedback


class PopulatorTypeformMixin:

    def create_typeforms(self, linked_object, typeforms_list):
        for typeform_data in typeforms_list:
            GenericTypeformFeedback.create_typeform(
                linked_object=linked_object,
                slug=typeform_data.get('slug'),
                typeform_id=GENERIC_TYPEFORMS.get(typeform_data.get('slug')),
                url=typeform_data.get('url', None),
            )
