from fastapi import FastAPI, APIRouter, HTTPException

router = APIRouter()


@router.get('/patient/info')
def demo_patient_info() -> dict:
    return {
        'name': 'aaa',
        'age': 'bbb',
    }


@router.get('/patient/gait/data')
def demo_patient_info() -> dict:
    return {
        'stride_length': 100,
        'stride_width': 200,
    }