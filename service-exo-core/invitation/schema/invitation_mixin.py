class InvitationMixin():

    def resolve_extra_data(self, info):
        return self.extra_data(info.context.user)

    # This is something strange, really I think is a bug, because
    # graphene build different classes for InvitationStatus and InvitationType,
    # one for InvitationNode and another for PublicInvitationNode
    def resolve_inv_status(self, info):
        return self.status

    def resolve_inv_type(self, info):
        return self.type
