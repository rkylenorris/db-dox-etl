from app_settings import get_app_settings
from sqlalchemy import create_engine, text

from sqlalchemy.orm import sessionmaker, Session

# create/get app settings
settings = get_app_settings()

# create connection string
if not settings.dox_db:
    raise ValueError("Database settings are not configured properly.")

CONNECTION_STRING = settings.dox_db.connection_string

# Create the SQLAlchemy engine and session factory
engine = create_engine(CONNECTION_STRING, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# function to expose for getting a database session
def get_db_session() -> Session:
    """Get a new database session.
    Returns:
        Session: A new SQLAlchemy session.
    """
    return SessionLocal()


# function to test the database connection
def connection_test() -> bool:
    """
    Test if database can connect.
    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    test_result = False
    try:
        connection = engine.connect()
        test_result = True
        connection.close()
    except Exception as e:
        test_result = False
    return test_result
