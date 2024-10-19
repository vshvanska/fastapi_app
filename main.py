from fastapi import FastAPI
from src.auth.routers import user_router
from src.comments.routers import comment_router
from src.posts.routers import post_router

app = FastAPI()


app.include_router(user_router)
app.include_router(post_router)
app.include_router(comment_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
