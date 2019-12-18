def get_curated_content(file_tuple):
    """
    .ics files need some headers to be parsed by the email backend
    however, email clients does not support those headers within
    the ics body content. This method removes the headers to make
    the attached file legible for the email clients.
    """
    if not type(file_tuple) == tuple:
        raise TypeError

    if type(file_tuple[1]) == bytes:
        try:
            content = str(file_tuple[1], 'utf-8')
        except UnicodeDecodeError:
            content = file_tuple[1]
    else:
        content = file_tuple[1]

    pattern = 'BEGIN:VCALENDAR'
    if type(content) == str and content.find(pattern) != -1:
        parts = content.split(pattern)
        content = '{}{}'.format(pattern, parts[1])

    return content
