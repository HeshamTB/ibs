
from .database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

EMERG_TEMP = 50
EMERG_SMOKE = 1000
T_HOUR_SEC = 3600
