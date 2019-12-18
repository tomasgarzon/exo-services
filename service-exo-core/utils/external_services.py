urls = {
    'exo-website-create-page': '/api/landing/page/',
    'exo-website-delete-page': '/api/landing/page/{uuid}/',
    'media-library-resource-list': 'api/resources/library',
    'media-library-resource-project-list': 'api/resources/library-project',
    'media-library-post-save-project': 'api/resources/post-save-project',
    'create-conversation-group': 'api/{uuid}/conversations/create-group/',
    'opportunities-add-user-permission': 'api/user/{uuid}/add-permission/',
    'opportunities-remove-user-permission': 'api/user/{uuid}/remove-permission/',
    'create-opportunities-group': 'api/group/',
}


def reverse(name, **kwargs):
    return urls.get(name).format(**kwargs)
