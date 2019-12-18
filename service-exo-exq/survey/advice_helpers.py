TEXT_1 = 'The model of your organization seems to be structured primarily around scarcity and/or you have few or no sources of abundance for your business. Exponential Organizations tap or create abundance of data, people, assets using different attributes (MTP, S, C, A, L, E)'  # noqa
TEXT_2 = 'You have few or no ExO attributes. The ExO Model can help you find ways to have a 10X growth or impact and/or scale faster'  # noqa
TEXT_3 = 'Your business model type is limiting your possibilities of exponential growth or impact'  # noqa
TEXT_4 = 'You are on your way to exponentiality. An Ecosystem business model type and tapping on a powerful combination of ExO attributes is key to unlock your exponentiality'  # noqa
TEXT_5 = 'Even when you have implemented certain ExO attributes, your potential is limited by the combination of ExO Attributes you have chosen. A powerful combination of ExO attributes is key to unlock exponentiality. For example, if you implement Staff on Demand but do not have a proper interface to manage it, you will not be able to make the most out of the leverage that relying on Staff on Demand can give you.'  # noqa


def get_advices(survey_filled):
    advices = []
    abundance_factor = survey_filled.abundance_factors()
    if sum(abundance_factor) <= 1:
        advices.append(TEXT_1)
