from utils.ratings import (
    update_interaction_from_answer,
    update_interaction_from_team_step)


def post_save_overall_rating_answer_handler(sender, answer, *args, **kwargs):
    user = answer.created_by
    update_interaction_from_answer(answer, user)


def post_save_overall_rating_team_step_handler(
        sender, consultant, team_step, relation_type, *args, **kwargs):
    update_interaction_from_team_step(
        team_step, consultant, relation_type)
