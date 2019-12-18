import graphene
from graphene_django.debug import DjangoDebug

import consultant.schema
import customer.schema
import core.schema  # noqa
import invitation.schema  # noqa
import relation.schema  # noqa
import industry.schema  # noqa
import exo_attributes.schema  # noqa
import project.schema  # noqa
import team.schema  # noqa
import custom_auth.schema  # noqa
import files.schema  # noqa
import utils.contrib  # noqa
import partner.schema  # noqa
import keywords.schema  # noqa
import exo_area.schema  # noqa
import achievement.schema  # noqa
import learning.schema  # noqa
import exo_hub.schema  # noqa
from utils.schema import CustomNode


class Query(
        consultant.schema.Query,
        customer.schema.Query,
        invitation.schema.Query,
        project.schema.Query,
        custom_auth.schema.Query,
        partner.schema.Query,
        exo_area.schema.Query,
        exo_hub.schema.Query,
        graphene.ObjectType
):

    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    debug = graphene.Field(DjangoDebug, name='__debug')

    class Meta:
        interfaces = (CustomNode, )


schema = graphene.Schema(query=Query)


class PublicQuery(
        project.schema.PublicQuery,
        invitation.schema.PublicQuery,
        graphene.ObjectType
):

    class Meta:
        interfaces = (graphene.relay.Node, )


public_schema = graphene.Schema(query=PublicQuery)
