from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from routers import user, healthcheck
import config

app = FastAPI()

# CORS protection
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=config.CORS_ALLOW_METHODS,
    allow_headers=config.CORS_ALLOW_HEADERS,
)
app.include_router(user.router)
app.include_router(healthcheck.router)

# skipcq: TCV-001 - This is the main entry point of the application
if __name__ == "__main__":
    if config.IS_DEVELOPMENT:
        from migrations import create_db_and_tables

        create_db_and_tables()
    uvicorn.run(app, host=config.HOST, port=int(config.PORT))
