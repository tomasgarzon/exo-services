urls = {
    'exo-lever-partner-list': '/api/partner/list/',
    'exo-lever-customer-list': '/api/customer/list/',
    'media-library-resource-list': '/api/resources/library',
    'media-library-resource-project-list': '/api/resources/library-project',
    'media-library-post-save-project': '/api/resources/post-save-project',
}


def reverse(name, **kwargs):
    return urls.get(name).format(**kwargs)
