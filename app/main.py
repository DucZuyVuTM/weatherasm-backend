import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import APP_NAME, APP_VERSION
from app.database import create_tables
from app.routers import auth, users, locations, weather


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    print("Tables created successfully")
    yield
    print("Shutting down application...")


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "## 🌤️ Weather Analysis & Forecasting Web Service\n\n"
        "REST API for real-time weather data, 7-day forecasts, statistical analysis, "
        "weather alerts, and multi-city comparisons — powered by **Open-Meteo** (no API key required).\n\n"
        "### Features\n"
        "- 🔐 JWT-based user authentication\n"
        "- 📍 Personal saved locations\n"
        "- 🌡️ Current weather for any city\n"
        "- 📅 7–16 day forecasts\n"
        "- ⚠️ Automatic weather alerts (wind, rain, snow, heat, cold, thunderstorm)\n"
        "- 📊 Historical statistics (avg/min/max/std)\n"
        "- 🗺️ Multi-city side-by-side comparison\n"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

PRODUCTION_ORIGIN = os.getenv("PRODUCTION_ORIGIN", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[PRODUCTION_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(locations.router)
app.include_router(weather.router)
