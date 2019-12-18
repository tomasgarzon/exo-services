class RequiredFieldsMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fields_required = getattr(self.Meta, 'fields_required', None)

        if fields_required:
            for key in self.fields:
                if key in fields_required:
                    self.fields[key].required = True
