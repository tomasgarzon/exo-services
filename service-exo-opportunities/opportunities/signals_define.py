from django.dispatch import Signal

opportunity_post_send = Signal(providing_args=['opportunity'])
opportunity_send_to_user = Signal(providing_args=['opportunity', 'user'])
opportunity_post_removed = Signal(providing_args=['opportunity', 'comment'])
opportunity_post_edited = Signal(providing_args=[
    'opportunity', 'comment', 'send_notification'])
opportunity_post_selected = Signal(providing_args=['opportunity', 'applicant'])
opportunity_post_rejected = Signal(providing_args=['opportunity', 'applicant'])
opportunity_post_closed = Signal(
    providing_args=['opportunity', 'user_list', 'origin'])
opportunity_new_applicant = Signal(providing_args=['opportunity', 'applicant'])
opportunity_status_changed = Signal(
    providing_args=['request', 'status', 'previous_status'])
signal_create_new_conversation = Signal(
    providing_args=['opportunity', 'user_from', 'message', 'files', 'user_to'])
opportunity_deadline = Signal(
    providing_args=['opportunity', 'deadline_date'])
opportunity_positions_covered = Signal(
    providing_args=['opportunity'])
send_message_to_conversation = Signal(
    providing_args=['applicant', 'message'])
opportunity_feedback_left = Signal(
    providing_args=['opportunity', 'applicant', 'user_from'])
