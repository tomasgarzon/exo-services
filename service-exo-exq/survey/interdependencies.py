from django.conf import settings

INTERDENPENDENCIES_VALUES = {
    settings.SURVEY_CH_MTP: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    settings.SURVEY_CH_STAFF_ON_DEMAND: [
        settings.SURVEY_CH_MTP, 1, 1, 1, 1,
        settings.SURVEY_CH_ENGAGEMENT,
        settings.SURVEY_CH_INTERFACES, 1, 1,
        settings.SURVEY_CH_AUTONOMY,
        settings.SURVEY_CH_SOCIAL],
    settings.SURVEY_CH_COMMUNITY_CROUD: [
        settings.SURVEY_CH_MTP,
        settings.SURVEY_CH_STAFF_ON_DEMAND, 1, 1, 1,
        settings.SURVEY_CH_ENGAGEMENT,
        settings.SURVEY_CH_INTERFACES, 1, 1,
        settings.SURVEY_CH_AUTONOMY,
        settings.SURVEY_CH_SOCIAL],
    settings.SURVEY_CH_ALGORITHMS_DATA: [
        1, 1, 1, 1, 1,
        settings.SURVEY_CH_ENGAGEMENT,
        settings.SURVEY_CH_INTERFACES,
        1, 1, 1, 1],
    settings.SURVEY_CH_LEVERAGED_ASSETS: [
        1, 1, 1, 1, 1, 1,
        settings.SURVEY_CH_INTERFACES,
        1, 1, 1, 1],
    settings.SURVEY_CH_ENGAGEMENT: [
        settings.SURVEY_CH_MTP,
        settings.SURVEY_CH_STAFF_ON_DEMAND, 1,
        settings.SURVEY_CH_ALGORITHMS_DATA, 1, 1,
        settings.SURVEY_CH_INTERFACES,
        1, 1, 1, 1],
    settings.SURVEY_CH_INTERFACES: [
        1, 1, 1, 1,
        settings.SURVEY_CH_LEVERAGED_ASSETS,
        1, 1, 1, 1, 1, 1],
    settings.SURVEY_CH_DASHBOARDS: [
        1, 1, 1, 1,
        settings.SURVEY_CH_LEVERAGED_ASSETS,
        1, 1, 1, 1, 1, 1],
    settings.SURVEY_CH_EXPERIMENTATION: [
        1, 1, 1,
        settings.SURVEY_CH_ALGORITHMS_DATA,
        1, 1, 1, 1, 1, 1, 1],
    settings.SURVEY_CH_AUTONOMY: [
        1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1],
    settings.SURVEY_CH_SOCIAL: [
        1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1],
}
