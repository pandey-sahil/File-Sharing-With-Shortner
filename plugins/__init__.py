
from aiohttp import web
from .route import routes
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def web_server():
    """Creates and returns an aiohttp web application with defined routes."""
    try:
        # Initialize the web application with a maximum client size of 30MB
        web_app = web.Application(client_max_size=30000000)
        
        # Add routes to the web application
        web_app.add_routes(routes)
        
        logger.info("Web server initialized successfully.")
        
        return web_app
    except Exception as e:
        logger.error(f"Error initializing the web server: {str(e)}")
        raise
