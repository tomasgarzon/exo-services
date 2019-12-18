from django.conf import settings


class AttachmentWrapper:
    filename = ''
    _source = None

    def __init__(self, file):
        self._source = file

    def set_filename(self, name):
        self.filename = name

    def get_filename(self):
        return self.filename

    def get_source(self):
        if self._source is None:
            raise NotImplementedError
        return self._source


class FileLocalWrapperMixin:

    def set_source(self, file):
        self._source = file


class PDFWrapper(FileLocalWrapperMixin, AttachmentWrapper):
    content_type = 'application/pdf'

    def read(self):
        return self._source.read()

    def serialize(self):
        return (
            self.get_filename(),
            self.read().decode(settings.PAYMENTS_PDF_DECODE_ISO)
        )
