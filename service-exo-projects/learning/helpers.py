import json

from django.core.serializers.json import DjangoJSONEncoder

from .models import MicroLearning, MicroLearningAverage


def serialize_personal_quiz(microlearning_average):
    json_encoder = DjangoJSONEncoder()
    project = microlearning_average.get_project()

    step_microlearnings = MicroLearning.objects.filter_by_step(
        microlearning_average.step)
    teams = project.teams.all()

    # Old version socket data
    serialized_data = microlearning_average.serialize()

    # Append data for new socket version
    serialized_data['personalRating'] = serialized_data.get('user')
    serialized_data['teamRatings'] = []

    for microlearning in step_microlearnings:
        for team in teams.filter(stream=microlearning.step_stream.stream):
            team_microlearning_avg = MicroLearningAverage(
                step_stream=microlearning.step_stream,
                user=None,
                team=team
            )
            data = team_microlearning_avg.serialize()
            serialized_data['teamRatings'].append(
                json.loads(
                    json_encoder.encode({
                        'pkTeam': team.pk,
                        'nameTeam': team.name,
                        'ratings': data.get('ratings'),
                        'avg': data.get('allTeamAvg'),
                    })
                )
            )
    serialized_data['teamRatings'] = sorted(
        serialized_data['teamRatings'], key=lambda x: x['pkTeam'])
    return serialized_data
