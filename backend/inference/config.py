from algorithms._analyzer import Analyzer
from algorithms.gait_basic.main import BasicGaitAnalyzer


MAPPING = {
    'gait_precomputed_csv_and_mp4': {
        'gait_basic::v1': BasicGaitAnalyzer,
    }
}


def data_and_model_map_to_class(data_type: str, model_name: str) -> Analyzer:
    return MAPPING[data_type][model_name]
