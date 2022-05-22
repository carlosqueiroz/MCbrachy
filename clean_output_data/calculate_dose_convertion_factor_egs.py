from egs_brachy_file_generator.LDR_brachy.seed_templates import iodine125_select_seed


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


def calculate_dose_rate_conversion_factor_with_know_caracteristics(source_model, treatment_kerma_rate):
    if source_model == "SelectSeed":
        air_kerma_str = iodine125_select_seed.AIR_KERMA_STRENGTH
    else:
        raise NotImplementedError

    return calculate_dose_rate_conversion_factor(treatment_kerma_rate, air_kerma_str)


def calculate_total_dose_conversion_factor_with_know_caracteristics(source_model, treatment_kerma_rate, treatment_time):
    if source_model == "SelectSeed":
        air_kerma_str = iodine125_select_seed.AIR_KERMA_STRENGTH
    else:
        raise NotImplementedError

    return calculate_total_dose(treatment_kerma_rate, air_kerma_str, treatment_time)
