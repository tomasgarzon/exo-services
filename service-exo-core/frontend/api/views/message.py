from rest_framework import generics
from rest_framework.response import Response
from django.contrib import messages
from django.utils.six import text_type


class MessagesAPIView(generics.ListAPIView):
    swagger_schema = None

    def get_queryset(self):
        return messages.get_messages(self.request)

    def get(self, request, format=None):
        messagelist = []
        for message in self.get_queryset():
            messagelist.append({
                'level': message.level,
                'message': text_type(message.message),
                'tags': message.tags,
            })
        return Response(messagelist)
