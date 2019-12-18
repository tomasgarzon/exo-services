from actstream import action


class ActionLogMixin:

    def get_logs(self, verb=None):
        logs = self.action_object_actions.all()

        if verb:
            logs = logs.filter(verb=verb)

        return logs

    def create_log(self, user_from, verb, description=None):
        return action.send(
            user_from,
            action_object=self,
            verb=verb,
            description=description)
