from fastapi import FastAPI
from router import user

app = FastAPI()

@app.get('/')
async def start():
    return "the project is starting..."

app.include_router(user.router)