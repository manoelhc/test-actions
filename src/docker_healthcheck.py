import requests
import sys

if __name__ == "__main__":
    response = requests.get("http://127.0.0.1:5000/health")
    if response.status_code == 200:
        print("Healthcheck passed")
        sys.exit(0)
    else:
        print("Healthcheck failed")
        sys.exit(1)
