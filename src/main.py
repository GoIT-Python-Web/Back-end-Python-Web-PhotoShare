from src.core.database import SessionLocal
from src.services.init_db import create_first_admin

def init():
    db = SessionLocal()
    create_first_admin(db)
    db.close()

init()

#####
import asyncio
from fastapi import FastAPI
from src.services.init_db import create_first_admin
from src.core.database import AsyncSessionLocal

app = FastAPI()

async def init():
    async with AsyncSessionLocal() as db:
        await create_first_admin(db)

@app.on_event("startup")
async def startup_event():
    await init()
