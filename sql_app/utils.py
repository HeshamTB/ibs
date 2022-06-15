# May 2022
# Hesham T. Banafa <hishaminv@gmail.com>

from .database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

EMERG_TEMP = 50
EMERG_SMOKE = 1000
EMERG_OPEN_TIME_SEC = 500

