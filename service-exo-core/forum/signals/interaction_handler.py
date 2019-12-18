from utils.ratings import update_interaction_from_answer


def post_save_overall_rating_answer_handler(sender, answer, *args, **kwargs):
    user = answer.created_by
    update_interaction_from_answer(answer, user)
