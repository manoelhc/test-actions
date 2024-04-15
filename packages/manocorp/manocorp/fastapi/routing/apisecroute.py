from collections.abc import Callable
from fastapi import Request, Response
from fastapi.routing import APIRoute

class SecFetchJsonRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            response: Response = await original_route_handler(request)
            response.headers["Content-Type"] = "application/json"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Sec-Fetch-Dest"] = "json"
            response.headers["Sec-Fetch-Site"] = "same-origin"
            response.headers["Sec-Fetch-Mode"] = "cors"

            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response

        return custom_route_handler
