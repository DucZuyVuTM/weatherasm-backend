"""
Generate an ER diagram (diagram.png) from the SQLAlchemy models.
Usage:
    python gen_erd.py
Requires: eralchemy2, a valid DATABASE_URL in .env
"""
from eralchemy2 import render_er
from app.database import Base
from app.models import user, location, weather_record, forecast

if __name__ == "__main__":
    render_er(Base, "diagram.png")
    print("diagram.png generated successfully")
