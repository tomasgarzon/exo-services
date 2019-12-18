class FocusFieldMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        focus = getattr(self.Meta, 'focus', None)
        if focus:
            self.fields[focus].widget.attrs.update({'autofocus': 'autofocus'})
