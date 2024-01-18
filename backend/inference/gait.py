import os

from models import ResultModel
from schemas.result import ResultSchema
from .config import data_and_model_map_to_class


result_schema = ResultSchema()


def inference_gait(
    dataType,
    modelName,
    submitUUID,
    session,
    trial_id,
):
    try:
        analyzer = data_and_model_map_to_class(data_type=dataType, model_name=modelName)()
    except Exception:
        raise ValueError(f'dataType={dataType} and modelName={modelName} not exist')
    # analyzer = BasicGaitAnalyzer()
    results = analyzer.run(
        data_root_dir=os.path.join('/root/backend/data/', submitUUID),
        file_id=trial_id,
    )
    # print(results)

    for result in results:
        form_date = result_schema.load({
            'requestUUID': submitUUID,
            'resultKey': result['key'],
            'resultValue': str(result['value']),
            'resultType': result['type'],
            'resultUnit': result['unit'],
        })
        resultObj = ResultModel(**form_date)
        session.add(resultObj)
        session.commit()
