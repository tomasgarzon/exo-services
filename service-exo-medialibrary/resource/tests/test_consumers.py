import pytest

from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer

from ..channels.consumers import LibraryWebsocketConsumer
from ..faker_factories import FakeResourceFactory
from ..api.serializers import ResourceListSerializer
from ..conf import settings


@pytest.mark.asyncio
async def test_library_websocket_connection():
    # PREPARE DATA
    communicator = WebsocketCommunicator(LibraryWebsocketConsumer, "/")

    # DO ACTION
    connected, subprotocol = await communicator.connect()

    # ASSERTS
    assert connected
    await communicator.disconnect()


@pytest.mark.asyncio
async def test_library_websocket_event():
    # PREPARE DATA
    communicator = WebsocketCommunicator(LibraryWebsocketConsumer, "/")
    connected, subprotocol = await communicator.connect()
    data = {"key": "value"}

    # DO ACTION
    await communicator.send_json_to(data)

    # ASSERTS
    response = await communicator.receive_json_from()
    assert response.get("key") == data.get("key")
    await communicator.disconnect()


@pytest.mark.asyncio
async def test_notificate_websocket_resource_available_event():
    # PREPARE DATA
    communicator = WebsocketCommunicator(LibraryWebsocketConsumer, "/")
    connected, subprotocol = await communicator.connect()
    layer = get_channel_layer()
    resource = FakeResourceFactory.create()
    resource_data = ResourceListSerializer(resource).data
    resource.set_as_available(False)

    # DO ACTION
    await layer.group_send(
        settings.RESOURCE_UPLOAD_WEBSOCKET_GROUP_NAME, {
            'type': 'video.updated',
            'pk': resource.pk
        })

    # ASSERTS
    response = await communicator.receive_json_from()
    assert response.get("type") == settings.RESOURCE_UPLOAD_WEBSOCKET_GROUP_NAME
    assert response.get("payload").get("status") == settings.RESOURCE_CH_STATUS_AVAILABLE
    assert response.get("payload").get("name") == resource_data.get("name")
    assert response.get("payload").get("description") == resource_data.get("description")
    assert response.get("payload").get("iframe") == resource_data.get("iframe")
    assert response.get("payload").get("duration") == resource_data.get("duration")
    await communicator.disconnect()
