class OpportunityUserMixin:

    def get_userBy(self, obj):
        return obj._serialize_user_by(
            obj.last_history.user,
            obj.last_history.created,
        )

    def get_userStatus(self, obj):
        return obj.user_status(
            self.context.get('request').user,
        ).__str__()

    def get_userActions(self, obj):
        return obj.user_actions(
            self.context.get('request').user,
        )


class OpportunityMixin:

    def get_numApplicants(self, obj):
        return obj.applicants_info.count()

    def get_alreadyVisited(self, obj):
        return obj.has_seen(self.context.get('request').user)

    def get_isNew(self, obj):
        return obj.is_new
