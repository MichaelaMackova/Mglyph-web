from typing import Union
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import sys
import os
# Add project root to sys.path (for absolute imports)
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__))) 

from db.database import create_db_and_tables
from settings import CORS_ORIGINS

# NOTE: Import routers
from api.heroes.router import router as heroes_router
from api.count.router import router as count_router
from api.auth.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup event
    create_db_and_tables()

    yield

    # shutdown event



app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}



app.include_router(count_router)
app.include_router(heroes_router)
