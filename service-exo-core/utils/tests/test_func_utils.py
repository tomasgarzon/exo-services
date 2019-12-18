from django import test

from utils.faker_factory import faker

from ..func_utils import infer_method_name, parse_urls


class FuncUtilsTest(test.TestCase):

    def test_infer_method_name(self):
        # INPUTS
        test_batch = [
            {
                'input': {
                    'method_to_infer': 'Test method',
                    'base_method': None,
                    'suffix': None,
                },
                'output': 'test_method',
            },

            {
                'input': {
                    'method_to_infer': '  Test   method   ',
                    'base_method': None,
                    'suffix': None,
                },
                'output': 'test_method',
            },

            {
                'input': {
                    'method_to_infer': '_test METHOD',
                    'base_method': None,
                    'suffix': None,
                },
                'output': '_test_method',
            },

            {
                'input': {
                    'method_to_infer': '_test METHOD',
                    'base_method': '',
                    'suffix': '',
                },
                'output': '_test_method',
            },

            {
                'input': {
                    'method_to_infer': 'Test method',
                    'base_method': 'get',
                    'suffix': None,
                },
                'output': 'get_test_method',
            },

            {
                'input': {
                    'method_to_infer': ' Test    Method',
                    'base_method': 'filter_by_test_method',
                    'suffix': None,
                },
                'output': 'filter_by_test_method_test_method',
            },

            {
                'input': {
                    'method_to_infer': ' Test    Method',
                    'base_method': 'filter_by_test_method',
                    'suffix': '_with_user',
                },
                'output': 'filter_by_test_method_test_method_with_user',
            },
        ]

        # DO ACTION
        for test_case in test_batch:
            self.assertEqual(
                infer_method_name(**test_case.get('input')),
                test_case.get('output'),
            )

    def test_parse_urls_with_html_tags(self):
        # PREPARE DATA
        faked_text = faker.text()
        faked_url = faker.url()
        faked_url_text = ' '.join(faker.words())
        text_to_parse = '<p>{}</p><a href="{}" rel="nofollow">{}</a>'.format(
            faked_text,
            faked_url,
            faked_url_text
        )

        # DO ACTION
        parsed_text = parse_urls(text_to_parse)

        # ASSERTIONS
        self.assertEqual(text_to_parse, parsed_text)

    def test_parse_urls_without_html_tags(self):
        # PREPARE DATA
        faked_url = faker.url()
        faked_text = faker.text()
        text_to_parse = '<p>{}</p>{}'.format(
            faked_text,
            faked_url
        )

        # DO ACTION
        text_parsed = parse_urls(text_to_parse)

        # ASSERTIONS
        self.assertEqual(
            '<p>{}</p><a href="{}" rel="nofollow">{}</a>'.format(
                faked_text,
                faked_url,
                faked_url),
            text_parsed
        )

    def test_parse_urls_with_complex_html(self):
        html = '<p><a href="https://wp.me/P1gdeo-iH?fbclid=IwAR3N6j5DvD8UWL-tIeeBitXUhM0tICGVEPtK8iPCvLHIqsb4vHA-QAgSf7U" target="_blank" style="color: rgb(54, 88, 153);"><img src="https://external.fcpt7-1.fna.fbcdn.net/safe_image.php?d=AQCUhfG5F2ZjQMzS&amp;w=540&amp;h=282&amp;url=https%3A%2F%2Fkevinianallen.files.wordpress.com%2F2018%2F11%2Fexolever_logo_rgb.jpg&amp;cfs=1&amp;upscale=1&amp;fallback=news_d_placeholder_publisher&amp;_nc_hash=AQD1LBjL0VmX0Mns" height="270" width="516"></a></p>'   # noqa
        text_parsed = parse_urls(html)

        self.assertIsNotNone(text_parsed)
