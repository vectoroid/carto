"""
Carto app - save your place in life
"""
import logging
# init logging
logger = logging.getLogger(__name__)

# app version
__version__ = "0.0.1"

# import app modules
from carto.api.config import AppSettings
from carto.api.types import Lon, Lat
from carto.api.models.geojson import Point
from carto.api.models.geojson import Props
from carto.api.models.geojson import Feature
from carto.api.models.geojson import FeatureCollection