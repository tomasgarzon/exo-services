from PIL import ImageFont, Image, ImageDraw

import os

from django.conf import settings

from io import BytesIO
from hashlib import md5
from math import sqrt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def background(text):
    """
        returns the background color based on the username md5
    """
    hash = md5(text.encode('utf-8')).hexdigest()
    hash_values = (hash[:8], hash[8:16], hash[16:24])
    bground = tuple(int(value, 16) % 256 for value in hash_values)
    return bground


def brightness(text):
    """
        returns the brightness of the background color
        explanation of the formula on
        http://www.nbdtech.com/Blog/archive/2008/04/27/\
        Calculating-the-Perceived-Brightness-of-a-Color.aspx
    """
    rCoef = 0.241
    gCoef = 0.691
    bCoef = 0.068
    bground = background(text)
    brightness = sqrt(rCoef * bground[0]**2 + gCoef * bground[1]**2 + bCoef * bground[2]**2)
    return brightness


def foreground(text):
    """
        returns black or white according to the brightness
    """
    bt = brightness(text)
    if bt > 130:
        return (0, 0, 0)
    else:
        return (255, 255, 255)


def create_image_profile(text, color=None, size=settings.EXO_ACCOUNTS_DEFAULT_IMAGE_SIZE, font_size=70):
    foreground_color = (255, 255, 255)
    if not color:
        color = background(text)
        foreground_color = foreground(text)
    img = Image.new(mode='RGBA', size=(size, size), color=color)
    url_font_medium = os.path.join(BASE_DIR, 'roboto/Roboto-Regular.ttf')
    font_nombre = ImageFont.truetype(url_font_medium, font_size)

    draw = ImageDraw.Draw(img)
    left_nombre = (img.size[0] - font_nombre.getsize(text)[0]) / 2.0
    top_nombre = (img.size[1] - font_nombre.getsize(text)[1]) / 2.0
    draw.text(
        (left_nombre, top_nombre - 5),
        text,
        foreground_color,
        font=font_nombre,
    )
    output = BytesIO()
    img.save(output, 'PNG')
    contents = output.getvalue()
    output.close()
    return contents
