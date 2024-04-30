from collections.abc import Callable
from fastapi import Request, Response
from fastapi.routing import APIRoute

class SecFetchJsonRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        """        Returns a custom route handler that adds specific headers to the response.

        This function returns a custom route handler that adds specific headers to the response obtained from the original route handler.

        Returns:
            Callable: A custom route handler function.
        """

        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """            Custom route handler for processing the request and modifying the response headers.

            This function takes a request object, processes it using the original route handler, and then modifies the response
            headers to include specific values for 'Content-Type', 'X-Content-Type-Options', 'Sec-Fetch-Dest', 'Sec-Fetch-Site',
            'Sec-Fetch-Mode', 'Cache-Control', 'Pragma', and 'Expires'.

            Args:
                request (Request): The request object to be processed.

            Returns:
                Response: The modified response object with updated headers.
            """

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
