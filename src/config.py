import dotenv
import os

dotenv.load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
