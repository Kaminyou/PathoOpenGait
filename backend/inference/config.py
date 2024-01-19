import typing as t

from algorithms._analyzer import Analyzer
from algorithms.gait_basic.main import SVOGaitAnalyzer


GAIT_PRECOMPUTED_CSV_AND_MP4_MODELS_SIMPLE = {
    'gait_svo::v1': SVOGaitAnalyzer,
}

MAPPING = {
    'gait_svo_and_txt': GAIT_PRECOMPUTED_CSV_AND_MP4_MODELS_SIMPLE,
}


def get_data_types() -> t.List[str]:
    data_types = []
    for k, _ in MAPPING.items():
        data_types.append(k)
    return data_types


def get_model_names(data_type: str) -> t.List[str]:
    models = MAPPING[data_type]
    model_names = []
    for k, _ in models.items():
        model_names.append(k)
    return model_names


def data_and_model_map_to_class(data_type: str, model_name: str) -> Analyzer:
    return MAPPING[data_type][model_name]
