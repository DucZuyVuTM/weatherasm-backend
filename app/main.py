from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import APP_NAME, APP_VERSION, PRODUCTION_ORIGIN
from app.infrastructure.database.session import create_tables
from app.presentation.routers import auth, users, locations, weather
from app.presentation.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[PRODUCTION_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(locations.router)
app.include_router(weather.router)


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
