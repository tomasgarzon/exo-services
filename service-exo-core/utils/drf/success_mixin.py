from django.contrib import messages


class SuccessMessageMixin(object):
    def get_success_message(self, cleaned_data):
        return self.success_message.format(cleaned_data)

    def set_success_message(self, data):
        success_message = self.get_success_message(data)
        messages.success(self.request._request, success_message)

    def set_message(self, message):
        messages.success(self.request._request, message)
