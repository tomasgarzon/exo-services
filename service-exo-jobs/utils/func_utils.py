import re


def infer_method_name(method_to_infer, base_method=None, suffix=None):
    return '{}{}{}'.format(
        '{}_'.format(base_method) if base_method else '',
        re.sub(' +', ' ', method_to_infer).strip().lower().replace(' ', '_'),
        suffix if suffix else '',
    )
