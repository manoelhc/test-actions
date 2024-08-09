import dotenv
import os

dotenv.load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = os.getenv("PORT", "5000")
PROTOCOL = os.getenv("PROTOCOL", "http")
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
CORS_ALLOW_METHODS = os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE").split(",")
CORS_ALLOW_HEADERS = os.getenv("CORS_ALLOW_HEADERS", "*").split(",")
PASSWORD_SALT = os.getenv("PASSWORD_SALT", "secret")
IS_DEVELOPMENT = ENVIRONMENT == "development"
TEST_USERNAME = os.getenv("TEST_USERNAME", "test_user")
TEST_USEREMAIL = os.getenv("TEST_USEREMAIL", "test_user@gmail.com")
