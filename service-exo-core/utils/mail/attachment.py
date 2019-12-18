import requests
import io


class AttachmentWrapper:
    name = ''
    _source = None

    def __init__(self, name):
        self.name = name

    def get_source(self):
        if self._source is None:
            raise NotImplementedError
        return self._source

    def set_source(self, source):
        self._source = source


class FileRemoteWrapperMixin:
    def set_source(self, source):
        try:
            file = requests.get(source)
        except requests.exceptions.ConnectionError:
            return None
        self._source = io.BytesIO()
        self._source.write(file.content)
        return self._source


class OfficeWrapper(FileRemoteWrapperMixin, AttachmentWrapper):
    content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    filename = 'file.docx'

    def read(self):
        return self.get_source().getvalue()

    def set_filename(self, name):
        self.filename = name

    def get_filename(self):
        return self.filename

    def as_string(self):
        return self.read()


class ICSWrapper(AttachmentWrapper):
    content_type = 'text/calendar'

    def read(self):
        return self.get_source().to_ical()

    def display(self):
        return self.read().decode('utf-8').replace('\r\n', '\n').strip()
