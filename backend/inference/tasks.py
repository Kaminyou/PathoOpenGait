import os

from celery import Celery
from celery.exceptions import MaxRetriesExceededError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from enums.request import Status
from models import RequestModel

from .gait import inference_gait


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")


@celery.task(bind=True, name='inference_gait_task', default_retry_delay=60)
def inference_gait_task(self, submitUUID: str):
    print(submitUUID)
    """
    The gait inference process
    """
    # STEP 1: Change status to COMPUTING
    engine = create_engine(
        os.getenv(
            'SQLALCHEMY_DATABASE_URI',
        )
    )
    Session = sessionmaker(bind=engine)
    session = Session()
    request_instance = session.query(RequestModel).filter_by(
        submitUUID=submitUUID).first()
    request_instance.status = Status.COMPUTING
    session.commit()

    # STEP 2: CROPPING
    dataType = request_instance.dataType
    modelName = request_instance.modelName

    try:
        inference_gait(
            dataType=dataType,
            modelName=modelName,
            submitUUID=submitUUID,
            session=session,
        )

        request_instance = session.query(RequestModel).filter_by(
            submitUUID=submitUUID).first()
        request_instance.status = Status.DONE
        session.commit()

    except Exception as e:
        request_instance = session.query(RequestModel).filter_by(
            submitUUID=submitUUID).first()
        request_instance.status = Status.ERROR
        request_instance.statusInfo = str(e)[:75]
        session.commit()
        return True

    return True

