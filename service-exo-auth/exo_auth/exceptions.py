class InactiveAccountException(Exception):
    """Raised when an account is required to be active.
    .. todo:: is InactiveAccount being used?
    """
    pass


class AlreadyVerifiedException(Exception):
    """Raised when a verfication request is made for an e-mail address
    that is already verified."""
    pass


class InvalidKeyException(Exception):
    """
        Raised when a verfication request is made for an invlaid verif key.
    """
    pass
