from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from src.openjarvis.logger import logger

class StatusResponse(BaseModel):
    """System status response model."""
    engine: str
    phase: str
    status: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """OpenJarvis lifecycle management."""
    logger.info("OpenJarvis engine initialized")
    yield
    logger.info("OpenJarvis engine shutdown")

app = FastAPI(lifespan=lifespan)

@app.get("/system/status", response_model=StatusResponse)
async def get_system_status() -> StatusResponse:
    """Check engine phase and operational status.

    @return: StatusResponse containing engine name, phase and current state.
    """
    logger.info("System status endpoint accessed.")
    return StatusResponse(
        engine="OpenJarvis",
        phase="2.A",
        status="online"
    )
