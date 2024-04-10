import requests
import sys
import config


def check_health(port: str = config.PORT):
    # skipcq: FLK-W505
    """
    Check the health of a service by sending a GET request to the health
    endpoint, inside the container.

    Args:
        port (int): The port number on which the service is running.
                    Defaults to config.PORT.

    Returns:
        bool: True if the healthcheck passes (status code 200),
              False otherwise.
    """
    try:
        url = f"{config.PROTOCOL}://{config.HOST}:{port}/health"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            print("Healthcheck passed")
            return True
        print("Healthcheck failed")
        return False
    except requests.exceptions.ConnectionError:
        print("Healthcheck failed")
        return False


if __name__ == "__main__" and not check_health():
    sys.exit(1)
