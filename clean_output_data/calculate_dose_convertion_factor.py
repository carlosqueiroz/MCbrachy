KNOWN_SOURCES = {}


def calculate_dose_rate_conversion_factor(treatment_kerma_rate, simulation_kerma_strength):
    """

    :param treatment_kerma_rate: muGy/h at 1m
    :param simulation_kerma_strength: muGym^2/histories

    :return: convertion factor
    """
    return treatment_kerma_rate / simulation_kerma_strength


def calculate_total_dose(treatment_kerma_rate, simulation_kerma_strength, treatment_time):
    """

    :param treatment_kerma_rate:
    :param simulation_kerma_strength:
    :param treatment_time: in h
    :return:
    """

    dose_rate = calculate_dose_rate_conversion_factor(treatment_kerma_rate, simulation_kerma_strength)

    return dose_rate * treatment_time


def calculate_dose_rate_conversion_factor_with_know_caracteristics(source_model):
    pass


def calculate_total_dose_conversion_factor_with_know_caracteristics(source_model):
    pass
