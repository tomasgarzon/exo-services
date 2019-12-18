import graphene


class MicrolearningAverageNode(graphene.ObjectType):
    user_avg = graphene.Int()
    team_avg = graphene.Int()
    user_project_avg = graphene.Int()
    team_project_avg = graphene.Int()
