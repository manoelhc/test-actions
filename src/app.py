from fastapi import FastAPI
import uvicorn
from routers import user, healthcheck
import config

# CORS protection
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS protection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user.router)
app.include_router(healthcheck.router)

if __name__ == "__main__":
    if config.ENVIRONMENT == "development":
        from migrations import create_db_and_tables

        create_db_and_tables()
    uvicorn.run(app, host="0.0.0.0", port=5000)
