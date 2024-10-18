from fastapi import FastAPI
from src.auth.routers import user_router

app = FastAPI()


app.include_router(user_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
