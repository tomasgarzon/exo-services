from django.dispatch import Signal


new_post_created = Signal(
    providing_args=['instance', 'raw', 'created', 'using', 'update_fields'],
    use_caching=True)

new_action_post = Signal(
    providing_args=['instance', 'action'], use_caching=True)

new_answer_created = Signal(
    providing_args=['instance', 'raw', 'created', 'using', 'update_fields'],
    use_caching=True)

new_action_answer = Signal(
    providing_args=['instance', 'action'], use_caching=True)

signal_post_overall_rating_answer_save = Signal(
    providing_args=['answer'])
