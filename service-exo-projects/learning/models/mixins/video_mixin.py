from embed_video.backends import detect_backend

from ...conf import settings


class MicroLearningVideoMixin:
    @property
    def video_id(self):
        backend = self.get_video_backend()
        return backend.code if backend else None

    def get_video_backend(self):
        return detect_backend(self.video) if self.video else None

    def get_video_iframe(self):
        backend = self.get_video_backend()
        return backend.get_embed_code(
            self.get_video_width(), self.get_video_height(),
        ) if backend else None

    def get_video_width(self):
        return settings.LEARNING_VIDEO_DEFAULT_WIDTH

    def get_video_height(self):
        return settings.LEARNING_VIDEO_DEFAULT_HEIGHT
