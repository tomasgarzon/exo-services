from utils.ratings import update_interaction_from_team_step


def post_save_overall_rating_team_step_handler(
        sender, user, team_step, relation_type, *args, **kwargs):
    update_interaction_from_team_step(
        team_step, user, relation_type)
