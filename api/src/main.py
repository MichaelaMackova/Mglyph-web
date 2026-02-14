from typing import Union
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import sys
import os
# Add project root to sys.path (for absolute imports)
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__))) 

from db.database import create_db_and_tables
from settings import CORS_ORIGINS, DEBUG_MODE, API_ROOT_PATH, AUTO_CREATE_TABLES


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup event
    if AUTO_CREATE_TABLES:
        create_db_and_tables()

    yield

    # shutdown event


# ===== Set metadata for OpenAPI =====

description = """
# Description
Mglyph-web API helps you do awesome stuff. 🚀

More description to come later...
"""

# Description of each tag for OpenAPI/Swagger UI
# order here defines the order in the documentation
tags_metadata = [
    {"name": "default", "description": "Default root path"},
    {"name": "auth", "description": "Authentication routes"},
    {"name": "heroes", "description": "Hero-related routes"},
    {"name": "count", "description": "Counting-related routes"},
    {"name": "challenges", "description": "Challenge-related routes"},
]

app = FastAPI(
    debug=DEBUG_MODE,
    lifespan=lifespan,

    title="Mglyph-web API",
    summary="Basic summary of Mglyph-web API",
    description=description,
    version="0.0.1",
    openapi_tags=tags_metadata,
    root_path=API_ROOT_PATH,
)



# ===== Enable CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Default paths =====

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}/")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}



# ===== API ROUTERS =====

# NOTE: Import routers
from api.heroes.router import router as heroes_router
from api.count.router import router as count_router
from api.auth.router import router as auth_router
from api.challenges.router import router as challenges_router

app.include_router(auth_router)
app.include_router(count_router)
app.include_router(heroes_router)
app.include_router(challenges_router)
