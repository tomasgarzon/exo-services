from django.conf import settings
from django.urls import re_path as url

from channels.routing import ProtocolTypeRouter, ChannelNameRouter, URLRouter

from utils.channels import AuthMiddlewareStack
from resource.channels.consumers import UploadChannelConsumer, LibraryWebsocketConsumer


application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            url(r"^library/$", LibraryWebsocketConsumer),
        ])
    ),
    "channel": ChannelNameRouter({
        settings.RESOURCE_UPLOAD_CHANNEL_NAME: UploadChannelConsumer,
    })
})
