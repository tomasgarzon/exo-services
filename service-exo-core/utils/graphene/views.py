from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.decorators import (
    authentication_classes,
    permission_classes,
    api_view,
)

from graphene_django.views import GraphQLView, HttpError
from graphql import parse

from utils.drf.authentication import CsrfExemptSessionAuthentication

from .document_ast import ast_depth


class CustomPublicGraphQLView(GraphQLView):

    MAX_DEPTH = 15

    def parse_body(self, request):
        try:
            data = super().parse_body(request)
        except HttpError:
            data = request._data
        try:
            document_ast = parse(data.get('query'))
            depth = ast_depth(document_ast.definitions[0])
            if depth > self.MAX_DEPTH:
                raise Exception('Max depth exceed')
        except AttributeError:
            pass
        return data

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class CustomAuthenticatedGraphQLViewGeneric(CustomPublicGraphQLView):
    permission_classes = (IsAuthenticated, )
    authenticate_classes = (SessionAuthentication, )
    method_allowed = ['POST']

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super().as_view(*args, **kwargs)
        view = permission_classes(cls.permission_classes)(view)
        view = authentication_classes(cls.authenticate_classes)(view)
        view = api_view(cls.method_allowed)(view)
        return view


class CustomAuthenticatedGraphQLView(CustomAuthenticatedGraphQLViewGeneric):
    method_allowed = ['GET', 'POST']


class CustomAuthenticatedJWTGraphQLView(CustomAuthenticatedGraphQLViewGeneric):
    authenticate_classes = (CsrfExemptSessionAuthentication, JSONWebTokenAuthentication, )
