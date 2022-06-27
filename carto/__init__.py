"""
Carto app - save your place in life
"""
import logging
# init logger
logger = logging.getLogger(__name__)

# app meta stuff
__version__ = "0.0.1"

# import app modules
from deta import Deta
from carto.api.config import get_app_config

# Get app config settings
settings = get_app_config()
