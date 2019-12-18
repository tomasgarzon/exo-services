from django.dispatch import Signal


signal_add_user_conversation = Signal(providing_args=['instance', 'user'])
signal_conversation_group_created = Signal(providing_args=['instance'])
signal_message_created = Signal(providing_args=['instance'])
signal_message_seen = Signal(providing_args=['instance'])
