from PIL import ImageFont, Image, ImageDraw
import argparse
import json
import dateutil.parser

ROBOTO_MEDIUM = 'roboto/Roboto-Medium.ttf'
ROBOTO_REGULAR = 'roboto/Roboto-Regular.ttf'
IMG_ORIGIN = 'banner_background.jpg'
IMG_DEST = '../hugo_site/static/img/banner.jpg'
IMAGE_WIDTH = 712
LEFT_MARGIN = 40


def IntelliDraw(drawer, text, font, containerWidth):
    words = text.split()
    lines = []
    lines.append(words)
    finished = False
    line = 0
    while not finished:
        thistext = lines[line]
        newline = []
        innerFinished = False
        while not innerFinished:
            if drawer.textsize(' '.join(thistext), font)[0] > containerWidth:

                newline.insert(0, thistext.pop(-1))
            else:
                innerFinished = True
        if len(newline) > 0:
            lines.append(newline)
            line = line + 1
        else:
            finished = True
    tmp = []
    for i in lines:
        tmp.append(' '.join(i))
    lines = tmp
    (width, height) = drawer.textsize(lines[0], font)
    return (lines, width, height)


def draw_text(draw, left, top, font, value):
    lines, _, h = IntelliDraw(
        draw,
        value,
        font,
        IMAGE_WIDTH)

    j = 0
    last_top = top
    for i in lines:
        draw.text(
            (left, top + j * h), i,
            font=font)
        j = j + 1
        last_top = top + j * h
    return last_top


def build_banner(name, speakers, location, date):

    img = Image.open(IMG_ORIGIN)

    draw = ImageDraw.Draw(img)
    last_top = draw_text(
        draw,
        LEFT_MARGIN,
        80,
        ImageFont.truetype(ROBOTO_MEDIUM, 56),
        name,
    )

    draw_text(
        draw,
        LEFT_MARGIN,
        last_top + 20,
        ImageFont.truetype(ROBOTO_REGULAR, 28),
        speakers,
    )

    draw_text(
        draw,
        LEFT_MARGIN,
        330,
        ImageFont.truetype(ROBOTO_MEDIUM, 32),
        date,
    )

    draw_text(
        draw,
        LEFT_MARGIN,
        365,
        ImageFont.truetype(ROBOTO_MEDIUM, 32),
        location,
    )

    ImageDraw.Draw(img)
    img.save(IMG_DEST, "JPEG")


def main(filename):
    with open(filename) as f:
        content = json.loads(f.read())
        speakers = [
            speaker.get('name') for speaker in content['speakers']]
        start = dateutil.parser.parse(content['start'])
        build_banner(
            content['name'],
            ' / '.join(speakers),
            content['location'],
            start.strftime('%d %b %Y'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Build banner for workshop')
    parser.add_argument(
        '-f', '--filename', help='Filename path', required=True)
    parser.add_argument(
        '-d', '--demo', help='Demo', required=False)
    args = parser.parse_args()

    if args.demo:
        build_banner(
            "The HOP Estrella Galicia Workshop",
            "Speaker Name / Speaker name / Speaker Name / Speaker name / Speaker Name",     # noqa
            "Granada, Spain",
            "18 Oct",
        )
    else:
        main(args.filename)
