from singleton_decorator import singleton

from qa_session.models import QASession

from .qa_session_builder import QASessionBuilder

from populate.populator.manager import Manager


@singleton
class QaSessionManager(Manager):
    model = QASession
    attribute = 'name'
    builder = QASessionBuilder
    files_path = '/qa_session/files/'
