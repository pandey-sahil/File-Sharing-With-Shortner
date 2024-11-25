from aiohttp import web

# Define the routes
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    """Handles GET and HEAD requests to the root URL."""
    response_data = {
        "message": "CodeXBotz"
    }
    return web.json_response(response_data)

async def init_app():
    """Initializes the web application."""
    app = web.Application()
    app.add_routes(routes)
    return app

if __name__ == "__main__":
    # Run the web server
    web.run_app(init_app(), port=8080)  # Change the port if needed
