from contextlib import contextmanager
from fastapi import  HTTPException, status
from db.config import SessionLocal

# Dependency to get the DB session
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        db.close()
