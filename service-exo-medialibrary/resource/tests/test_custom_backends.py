from django.test import TestCase

from embed_video.backends import detect_backend


class TestCustomBackendsTestCase(TestCase):

    def test_custom_backend_url_parser(self):
        # PREPARE DATA
        inputs = [
            "https://vimeo.com/4413241",
            "https://www.youtube.com/watch?v=GPB8ovFD_W4",
            "https://drive.google.com/open?id=1Lw7QrhBpYkZaXS8KATPEktjeND-kgX98",
            "https://www.dropbox.com/s/o6dnqzyhar647qu/gatos.mp4?dl=0"
        ]
        outputs = [
            "https://vimeo.com/4413241",
            "https://www.youtube.com/watch?v=GPB8ovFD_W4",
            "https://docs.google.com/uc?export=download&id=1Lw7QrhBpYkZaXS8KATPEktjeND-kgX98",
            "https://www.dl.dropboxusercontent.com/s/o6dnqzyhar647qu/gatos.mp4"
        ]

        # DO ACTION
        for index, url_video in enumerate(inputs):
            backend = detect_backend(url_video)

            # ASSERTS
            self.assertEqual(outputs[index], backend.get_url_parsed(url_video))
