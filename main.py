import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.core.logger import logger
from app.middleware.logging_middleware import LoggingMiddleware
from app.routes import auth, exams, results, monitoring

# Create all tables with retry (wait for MySQL to be ready)
if not os.environ.get("TESTING"):
    for attempt in range(15):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            break
        except Exception as e:
            logger.warning(f"DB not ready (attempt {attempt+1}/15): {e}")
            time.sleep(3)

app = FastAPI(
    title="Online Examination System",
    description="Backend API for managing online examinations",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.include_router(auth.router)
app.include_router(exams.router)
app.include_router(results.router)
app.include_router(monitoring.router)


@app.on_event("startup")
async def startup():
    logger.info("Online Examination System started successfully")


@app.get("/")
def root():
    return {"message": "Online Examination System API", "docs": "/docs"}