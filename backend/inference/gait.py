import os

from algorithms.gait_basic.main import BasicGaitAnalyzer
from schemas.result import ResultSchema
from models import ResultModel

result_schema = ResultSchema()


def inference_gait(
    dataType,
    modelName,
    submitUUID,
    session,
):
    analyzer = BasicGaitAnalyzer()
    results = analyzer.run(
        data_root_dir=os.path.join('/root/backend/data/', submitUUID),
        file_id='uploaded'
    )
    print(results)

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
