from fastapi import FastAPI
import uvicorn

from src.routes import comment_route

app = FastAPI()

app.include_router(comment_route.router)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
