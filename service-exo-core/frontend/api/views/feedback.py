from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import parsers

from utils.mail import handlers

from ..serializers.feedback import FeedbackSerializer
from ...conf import settings


class FeedbackAPIView(APIView):
    parser_classes = (parsers.MultiPartParser, )
    serializer_class = FeedbackSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        attachments = []
        if serializer.validated_data.get('attachment'):
            attachments.append(serializer.validated_data.get('attachment'))

        handlers.mail_handler.send_mail(
            'new_feedback',
            recipients=settings.FRONTEND_FEEDBACK_TO,
            name=request.user.get_full_name(),
            from_email=request.user.email,
            email=request.user.email,
            reply_to=[request.user.email],
            message=serializer.validated_data.get('message'),
            attachments=attachments,
        )
        return Response({})
