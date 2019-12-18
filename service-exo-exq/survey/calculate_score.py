from django.conf import settings

from .interdependencies import INTERDENPENDENCIES_VALUES

SCORE_MAX = 3
SCORE_MIN = 0.5
SCORE_THRESHOLD = 1.2
SCORE_ABUNDANCE_CORRECTION = 0.98
SCORE_NORMALISED_MAX = 100
SCORE_NORMALISED_MIN = 0
SCORE_RANGE = SCORE_NORMALISED_MAX - SCORE_NORMALISED_MIN


def apply_interdependency(results):
    for result in results:
        corrections = INTERDENPENDENCIES_VALUES.get(result.section)
        total = 1
        for value in corrections:
            if isinstance(value, int):
                total *= value
            else:
                interdependency = list(filter(lambda x: x.section == value, results))[0].interdependency
                total *= interdependency
        result.total_correction = total
        result.corrected_average = round(result.score * total, 2)


def normalize_attributes(results):
    for result in results:
        ratio_actual = result.score - SCORE_MIN
        ratio_threshold = SCORE_THRESHOLD - SCORE_MIN
        result.interdependency = round(ratio_actual / ratio_threshold, 2) if result.score < SCORE_THRESHOLD else 1.0


def calculate_correction_business_model(answers):
    business_model = answers.filter(
        question__section=settings.SURVEY_CH_BUSINESS_MODEL).first()
    return business_model.score


def calculate_corrected_score(survey_filled):
    answers = survey_filled.answers.all()
    correction_business_model = calculate_correction_business_model(answers)

    results = list(survey_filled.results.exclude(
        section=settings.SURVEY_CH_BUSINESS_MODEL))

    total_abundance_score = sum(
        map(lambda x: 1 if x.score >= 1.5 else 0, results))
    correction_abundance = 1 if total_abundance_score > 4 else SCORE_ABUNDANCE_CORRECTION

    normalize_attributes(results)
    apply_interdependency(results)

    corrected_total_average = round(
        sum(map(lambda x: x.corrected_average, results)) / len(results),
        2
    )
    total_average = round(
        sum(map(lambda x: x.score, results)) / len(results),
        1
    )
    correction_interdependency = round(
        corrected_total_average / total_average,
        2
    )
    _normalized_average = (total_average - SCORE_MIN) / (SCORE_MAX - SCORE_MIN)
    normalised_exq = round(
        _normalized_average * SCORE_RANGE + SCORE_NORMALISED_MIN,
        2
    )

    total_of_all_corrections = correction_business_model * correction_abundance * correction_interdependency
    return round(normalised_exq * total_of_all_corrections, 2)
