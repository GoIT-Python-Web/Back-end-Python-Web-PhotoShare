from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from src.routes import admin_route, comment_route, rating_route, post_route, auth

app = FastAPI()

app.include_router(admin_route.router)
app.include_router(comment_route.router)
app.include_router(rating_route.router)
app.include_router(post_route.router)
app.include_router(auth.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)