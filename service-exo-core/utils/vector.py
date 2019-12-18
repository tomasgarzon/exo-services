def textarea_to_vector(text):
    text_tmp = text
    if text_tmp.startswith('-'):
        text_tmp = '\r\n' + text_tmp
    return [_.strip() for _ in text_tmp.split('\r\n-') if _ != '']
