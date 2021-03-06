"""
file:  /main.py
        - entry script
        - required by Deta
"""
import logging
import typing

from datetime import datetime as dt
from uuid import UUID
from fastapi import Depends, FastAPI

from carto.api.config import get_app_config
from carto.api.tags import Tag
from carto.api.models.geojson import Feature
from carto.api.exceptions import NotFoundHTTPException
from carto.api.routers import features as FeaturesRouter
from carto.api.routers import tags as TagsRouter

# Configure and crank up the Logger
logger = logging.getLogger(__name__)

# Set application configuration
settings = get_app_config()
logger.info(f"Configuring {settings.title} app settings ...")
app_config = {
    "debug": settings.debug_mode,
    "dependencies": [Depends(get_app_config)],
    "description": settings.description,
    "title": settings.title,
    "root_path": settings.root_path,
    "version": settings.version
}
# initialize app
logger.info("Instantiating FastAPI ...")
app = FastAPI(**app_config)
# -> initialize routers
app.include_router(FeaturesRouter)
app.include_router(TagsRouter)

# API Index Route
@app.get('/')
async def get_api_root():
    return {"message": "Welcome to the Execas API!"}