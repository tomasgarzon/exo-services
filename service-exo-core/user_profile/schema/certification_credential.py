import graphene

from graphene_django import DjangoObjectType

from certification.models import CertificationCredential


class CertificationCredentialNode(DjangoObjectType):
    name = graphene.String()
    description = graphene.String()
    pdf = graphene.String()
    code = graphene.String()
    role_name = graphene.String()

    class Meta:
        model = CertificationCredential
        exclude_fields = ['pk']

    def resolve_code(self, info):
        return self.content_object.role.code

    def resolve_role_name(self, info):
        return self.content_object.role.name
