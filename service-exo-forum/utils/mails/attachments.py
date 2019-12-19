def fix_attachments(original_attachments=[]):
    attachments = []
    for attach in original_attachments:
        try:
            name, content = attach
        except (ValueError, TypeError):
            name = attach.get_filename()
            content = attach.as_string()
        new_content = (name, content)
        attachments.append(new_content)
    return attachments
