from django.utils import timezone
from django.contrib.auth import login as django_login
from django.shortcuts import redirect
from django.views.generic.base import View
from django.http import Http404

from .exceptions import InactiveAccountException, AlreadyVerifiedException
from .models import EmailAddress
from .settings import MM
from .signals_define import email_verified


class Verify(View):

    def get(self, request, email_pk, verif_key, next=MM.POST_VERIFY_URL):
        try:
            email = EmailAddress.objects.get(pk=email_pk, verif_key=verif_key)
            if email.is_verified:
                raise AlreadyVerifiedException()
            if not MM.ALLOW_VERIFICATION_OF_INACTIVE_ACCOUNTS and \
                    not email.user.is_active:
                raise InactiveAccountException()
            email.verified_at = timezone.now()
            email.save()
            email_verified.send_robust(sender=EmailAddress, instance=email)
            email.set_primary()

        except EmailAddress.DoesNotExist:
            raise Http404

        except InactiveAccountException:
            pass

        except AlreadyVerifiedException:
            pass

        django_login(
            request,
            email.user,
            backend='django.contrib.auth.backends.ModelBackend')
        return redirect(next)
