from time import sleep
import requests
import sys
import config


def check_health(port: str = config.PORT, endpoint: str = "/health"):
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
    url = f"{config.PROTOCOL}://{config.HOST}:{port}/{endpoint}"
    retry = 0
    max_retries = 3
    while True:
        if retry >= max_retries:
            break
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"Healthcheck passed: {url}")
                return True
        except requests.exceptions.ConnectionError:
            print(f"Healthcheck failed: {url}")
            return False
        retry = retry + 1
        sleep(1)

    print(f"Healthcheck failed: {url}")
    return False


# skipcq: TCV-001 - This is the main entry point of the application
if __name__ == "__main__" and not check_health():
    sys.exit(1)
