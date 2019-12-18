from django.contrib import messages


class DeleteMessageMixin(object):
    """
          Adds a delete message on successful object deletion.
    """
    delete_message = ''

    def get_delete_message(self):
        return self.delete_message % {'object': self.get_object()}

    def delete(self, request, *args, **kwargs):
        delete_message = self.get_delete_message()
        if delete_message:
            messages.success(request, delete_message)
        return super(DeleteMessageMixin, self).delete(request, *args, **kwargs)
