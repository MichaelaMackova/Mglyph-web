from typing import Union
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import sys
import os
# Add project root to sys.path (for absolute imports)
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__))) 

from errors import MGlyphApiError, MGlyphApiError_exception_handler, MGlyphApiError_http_exception_handler

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
    {"name": "challenges", "description": "Challenge-related routes"},
    {"name": "mglyph", "description": "Mglyph-related routes"},
    {"name": "users", "description": "User-related routes"},
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



# ===== Custom exception handling =====
app.add_exception_handler(MGlyphApiError, MGlyphApiError_exception_handler)
app.add_exception_handler(MGlyphApiError.HTTPException, MGlyphApiError_http_exception_handler)



# ===== Default paths =====

@app.get("/")
def read_root():
    return {"Hello": "World"}



# ===== API ROUTERS =====

# NOTE: Import routers
from api.auth.router import router as auth_router
from api.challenges.router import router as challenges_router
from api.users.router import router as users_router
from api.mglyph.router import router as mglyph_router
from api.file.router import router as file_router

app.include_router(auth_router)
app.include_router(challenges_router)
app.include_router(users_router)
app.include_router(mglyph_router)
app.include_router(file_router)
