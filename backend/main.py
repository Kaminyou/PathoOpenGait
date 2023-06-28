from fastapi import FastAPI, APIRouter, HTTPException

from routers import demo, admin

app = FastAPI()
api_router = APIRouter()
api_router.include_router(demo.router, prefix="/api/demo", tags=["demo"])
api_router.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@api_router.get("/api")
def root() -> dict:
    return {'msg': 'hello'}

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)