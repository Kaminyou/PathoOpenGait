from fastapi import FastAPI, APIRouter, HTTPException

router = APIRouter()


@router.get('/whoami')
def admin_info() -> dict:
    return {
        'msg': 'i am admin'
    }
