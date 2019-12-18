import re

from django.template.defaultfilters import urlize

from bs4 import BeautifulSoup as Soup


def infer_method_name(method_to_infer, base_method=None, suffix=None):
    return '{}{}{}'.format(
        '{}_'.format(base_method) if base_method else '',
        re.sub(' +', ' ', method_to_infer).strip().lower().replace(' ', '_'),
        suffix if suffix else '',
    )


def parse_urls(text_to_clean, autoescape=False):
    """
    Parse plain text urls to html tags
    """
    link_tags = Soup(text_to_clean, 'html.parser')
    mask_replace_text = '>{}</a>'
    mask_replace_link = 'href="{}"'

    for tag in link_tags.find_all('a'):
        link_text = re.findall(r'[^>]+(?=<)', str(tag))
        if link_text:
            link_text = link_text[0].replace(' ', '_')
            link = re.search(r'href=[\'\"]?([^\'\" >]+)', str(tag))
            if link:
                link_url = link.group(1)
                text_to_clean = text_to_clean.replace(
                    str(tag),
                    '{}|{}'.format(link_url, link_text),
                )

    text_to_clean = urlize(text_to_clean, autoescape).replace('%7C', '|')

    link_tags = Soup(text_to_clean, 'html.parser')
    for tag in link_tags.find_all('a'):
        url_text = re.findall(r'[^>]+(?=<)', str(tag))[0]
        link = url_text.split('|')[0]
        try:
            text = url_text.split('|')[1].replace('_', ' ')
            text_to_clean = text_to_clean.replace(
                mask_replace_link.format(url_text),
                mask_replace_link.format(link))
            text_to_clean = text_to_clean.replace(
                mask_replace_text.format(url_text),
                mask_replace_text.format(text))
        except IndexError:
            pass

    return text_to_clean
